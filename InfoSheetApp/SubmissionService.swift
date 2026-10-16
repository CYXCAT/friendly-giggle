import Foundation

struct SubmissionPayload: Encodable {
    let yourName: String
    let areYouACat: String
    let makesBiscuits: String
    let canPurr: String

    enum CodingKeys: String, CodingKey {
        case yourName = "your_name"
        case areYouACat = "are_you_a_cat"
        case makesBiscuits = "makes_biscuits"
        case canPurr = "can_purr"
    }
}

struct SubmissionResponse: Decodable {
    let success: Bool
    let row: Int
}

enum SubmissionError: LocalizedError {
    case invalidResponse
    case offline
    case server(String)

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "The server returned an invalid response."
        case .offline:
            return "The network is unavailable. Check your internet connection and try again."
        case .server(let message):
            return message
        }
    }
}

struct SubmissionService {
    private let baseURL: URL
    private let session: URLSession

    init() {
        let configured = Bundle.main.object(forInfoDictionaryKey: "API_BASE_URL") as? String
        self.baseURL = URL(string: configured ?? "https://example.invalid")!

        let configuration = URLSessionConfiguration.default
        configuration.waitsForConnectivity = true
        configuration.timeoutIntervalForRequest = 30
        self.session = URLSession(configuration: configuration)
    }

    func submit(_ payload: SubmissionPayload, googleIDToken: String) async throws -> SubmissionResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("submissions"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(googleIDToken)", forHTTPHeaderField: "Authorization")
        request.httpBody = try JSONEncoder().encode(payload)

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch let error as URLError where error.code == .notConnectedToInternet {
            throw SubmissionError.offline
        }
        guard let httpResponse = response as? HTTPURLResponse else {
            throw SubmissionError.invalidResponse
        }
        guard (200..<300).contains(httpResponse.statusCode) else {
            let detail = (try? JSONDecoder().decode(ServerError.self, from: data).detail)
            throw SubmissionError.server(detail ?? "Submission failed. Please try again.")
        }
        return try JSONDecoder().decode(SubmissionResponse.self, from: data)
    }
}

private struct ServerError: Decodable {
    let detail: String
}
