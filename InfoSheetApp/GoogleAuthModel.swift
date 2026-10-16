import Combine
import GoogleSignIn
import UIKit

@MainActor
final class GoogleAuthModel: ObservableObject {
    @Published private(set) var idToken: String?
    @Published private(set) var userName: String?
    @Published private(set) var email: String?
    @Published private(set) var isLoading = false
    @Published var errorMessage: String?
    @Published var showingError = false

    init() {
        restorePreviousSignIn()
    }

    func signIn() async {
        guard let presentingViewController else {
            showError("Unable to present Google sign-in.")
            return
        }

        isLoading = true
        defer { isLoading = false }

        do {
            let result = try await GIDSignIn.sharedInstance.signIn(
                withPresenting: presentingViewController
            )
            let user = try await result.user.refreshTokensIfNeeded()
            update(with: user)
        } catch {
            showError(error.localizedDescription)
        }
    }

    func signOut() {
        GIDSignIn.sharedInstance.signOut()
        idToken = nil
        userName = nil
        email = nil
    }

    private func restorePreviousSignIn() {
        GIDSignIn.sharedInstance.restorePreviousSignIn { [weak self] user, error in
            Task { @MainActor in
                if let user {
                    self?.update(with: user)
                } else if let error {
                    self?.showError(error.localizedDescription)
                }
            }
        }
    }

    private func update(with user: GIDGoogleUser) {
        idToken = user.idToken?.tokenString
        userName = user.profile?.name
        email = user.profile?.email
    }

    private func showError(_ message: String) {
        errorMessage = message
        showingError = true
    }

    private var presentingViewController: UIViewController? {
        let scene = UIApplication.shared.connectedScenes
            .compactMap { $0 as? UIWindowScene }
            .first { $0.activationState == .foregroundActive }
        return scene?.keyWindow?.rootViewController
    }
}
