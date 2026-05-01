import { useState } from "react";
import {
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

import { isSupabaseAuthConfigured, supabase } from "../auth/supabase";

export function AuthScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const canSubmit =
    isSupabaseAuthConfigured && email.trim().length > 0 && password.length >= 6 && !isLoading;

  const handleSignIn = async () => {
    if (!canSubmit) {
      return;
    }

    setIsLoading(true);
    setMessage(null);
    const { error } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password,
    });
    setIsLoading(false);

    if (error) {
      setMessage(error.message);
    }
  };

  const handleSignUp = async () => {
    if (!canSubmit) {
      return;
    }

    setIsLoading(true);
    setMessage(null);
    const { error } = await supabase.auth.signUp({
      email: email.trim(),
      password,
    });
    setIsLoading(false);

    if (error) {
      setMessage(error.message);
      return;
    }

    setMessage("Check your email if confirmation is enabled.");
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      style={styles.screen}
    >
      <View style={styles.panel}>
        <Text style={styles.appName}>Battry</Text>
        <Text style={styles.copy}>Sign in to keep your battery history tied to your account.</Text>

        {!isSupabaseAuthConfigured ? (
          <Text style={styles.error}>
            Supabase auth env vars are missing. Set EXPO_PUBLIC_SUPABASE_URL and
            EXPO_PUBLIC_SUPABASE_ANON_KEY.
          </Text>
        ) : null}

        <TextInput
          autoCapitalize="none"
          autoComplete="email"
          keyboardType="email-address"
          placeholder="email"
          placeholderTextColor="#8C8D86"
          style={styles.input}
          value={email}
          onChangeText={setEmail}
        />
        <TextInput
          autoCapitalize="none"
          autoComplete="password"
          placeholder="password"
          placeholderTextColor="#8C8D86"
          secureTextEntry
          style={styles.input}
          value={password}
          onChangeText={setPassword}
        />

        {message ? <Text style={styles.message}>{message}</Text> : null}

        <TouchableOpacity
          accessibilityRole="button"
          disabled={!canSubmit}
          style={[styles.primaryButton, !canSubmit ? styles.disabledButton : null]}
          onPress={handleSignIn}
        >
          <Text style={styles.primaryText}>{isLoading ? "Working" : "Sign in"}</Text>
        </TouchableOpacity>
        <TouchableOpacity
          accessibilityRole="button"
          disabled={!canSubmit}
          style={[styles.secondaryButton, !canSubmit ? styles.disabledSecondary : null]}
          onPress={handleSignUp}
        >
          <Text style={styles.secondaryText}>Create account</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: {
    backgroundColor: "#F7F7F2",
    flex: 1,
    justifyContent: "center",
    padding: 20,
  },
  panel: {
    backgroundColor: "#FFFFFF",
    borderColor: "#DADBD2",
    borderRadius: 8,
    borderWidth: 1,
    padding: 18,
  },
  appName: {
    color: "#151515",
    fontSize: 32,
    fontWeight: "900",
  },
  copy: {
    color: "#4F514C",
    fontSize: 15,
    lineHeight: 21,
    marginTop: 8,
  },
  input: {
    backgroundColor: "#FAFAF7",
    borderColor: "#DADBD2",
    borderRadius: 8,
    borderWidth: 1,
    color: "#151515",
    fontSize: 16,
    marginTop: 12,
    padding: 13,
  },
  error: {
    backgroundColor: "#FFE8E2",
    borderColor: "#D9482F",
    borderRadius: 8,
    borderWidth: 1,
    color: "#8D210F",
    marginTop: 14,
    padding: 12,
  },
  message: {
    color: "#4F514C",
    fontSize: 14,
    lineHeight: 20,
    marginTop: 12,
  },
  primaryButton: {
    alignItems: "center",
    backgroundColor: "#151515",
    borderRadius: 8,
    marginTop: 14,
    paddingVertical: 14,
  },
  disabledButton: {
    backgroundColor: "#9B9C95",
  },
  primaryText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "800",
  },
  secondaryButton: {
    alignItems: "center",
    borderColor: "#DADBD2",
    borderRadius: 8,
    borderWidth: 1,
    marginTop: 10,
    paddingVertical: 14,
  },
  disabledSecondary: {
    opacity: 0.55,
  },
  secondaryText: {
    color: "#151515",
    fontSize: 16,
    fontWeight: "800",
  },
});
