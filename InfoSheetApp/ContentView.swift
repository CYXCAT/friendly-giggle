import SwiftUI
import GoogleSignInSwift

private enum Answer: String, CaseIterable, Identifiable {
    case yes = "Yes"
    case no = "No"

    var id: Self { self }
}

struct ContentView: View {
    @StateObject private var auth = GoogleAuthModel()
    @State private var yourName = ""
    @State private var isCat: Answer = .yes
    @State private var makesBiscuits: Answer = .yes
    @State private var canPurr: Answer = .yes
    @State private var isSubmitting = false
    @State private var message: String?
    @State private var showingResult = false

    private let service = SubmissionService()

    var body: some View {
        NavigationStack {
            Form {
                if let idToken = auth.idToken {
                    Section("Signed in") {
                        if let email = auth.email {
                            Text(email)
                                .foregroundStyle(.secondary)
                        }
                        Button("Sign out", role: .destructive) {
                            auth.signOut()
                        }
                    }

                    Section("About you") {
                        TextField("Your name", text: $yourName)
                            .textContentType(.name)
                        answerPicker("Are you a cat?", selection: $isCat)
                        answerPicker("If so, do you make biscuits?", selection: $makesBiscuits)
                        answerPicker("Can you purrr?", selection: $canPurr)
                    }

                    Section {
                        Button {
                            submit(idToken: idToken)
                        } label: {
                            HStack {
                                Spacer()
                                if isSubmitting {
                                    ProgressView()
                                } else {
                                    Text("Submit")
                                        .fontWeight(.semibold)
                                }
                                Spacer()
                            }
                        }
                        .disabled(isSubmitting || yourName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                    }
                } else {
                    Section {
                        GoogleSignInButton {
                            Task {
                                await auth.signIn()
                            }
                        }
                        .frame(height: 48)
                        .disabled(auth.isLoading)
                    } footer: {
                        Text("Sign in with Google before submitting the form.")
                    }
                }
            }
            .navigationTitle("Info Sheet")
            .onChange(of: auth.userName) { _, newValue in
                if yourName.isEmpty {
                    yourName = newValue ?? ""
                }
            }
            .alert("Submission", isPresented: $showingResult) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(message ?? "")
            }
            .alert("Sign in", isPresented: $auth.showingError) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(auth.errorMessage ?? "Google sign-in failed.")
            }
        }
    }

    private func answerPicker(_ title: String, selection: Binding<Answer>) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
            Picker(title, selection: selection) {
                ForEach(Answer.allCases) { answer in
                    Text(answer.rawValue).tag(answer)
                }
            }
            .pickerStyle(.segmented)
        }
        .padding(.vertical, 4)
    }

    private func submit(idToken: String) {
        isSubmitting = true
        message = nil

        let payload = SubmissionPayload(
            yourName: yourName.trimmingCharacters(in: .whitespacesAndNewlines),
            areYouACat: isCat.rawValue,
            makesBiscuits: makesBiscuits.rawValue,
            canPurr: canPurr.rawValue
        )

        Task {
            do {
                let response = try await service.submit(payload, googleIDToken: idToken)
                message = "Saved to row \(response.row)."
            } catch {
                message = error.localizedDescription
            }
            isSubmitting = false
            showingResult = true
        }
    }
}

#Preview {
    ContentView()
}
