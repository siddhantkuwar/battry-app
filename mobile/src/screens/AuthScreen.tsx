import { StyleSheet, Text, TouchableOpacity, View } from "react-native";

type AuthScreenProps = {
  errorMessage: string | null;
  isSupabaseConfigured: boolean;
  onRetry: () => void;
};

export function AuthScreen({ errorMessage, isSupabaseConfigured, onRetry }: AuthScreenProps) {
  const setupMessage = isSupabaseConfigured
    ? (errorMessage ??
      "Anonymous auth is not ready. Check that it is enabled in Supabase Auth.")
    : "Set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY in mobile/.env.";

  return (
    <View style={styles.screen}>
      <View style={styles.panel}>
        <Text style={styles.appName}>Battry</Text>
        <Text style={styles.copy}>
          Battry uses a private device identity. There is no account, email, or password.
        </Text>

        <Text style={styles.error}>{setupMessage}</Text>

        <TouchableOpacity
          accessibilityRole="button"
          disabled={!isSupabaseConfigured}
          style={[styles.primaryButton, !isSupabaseConfigured ? styles.disabledButton : null]}
          onPress={onRetry}
        >
          <Text style={styles.primaryText}>Start private session</Text>
        </TouchableOpacity>
      </View>
    </View>
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
  error: {
    backgroundColor: "#FFE8E2",
    borderColor: "#D9482F",
    borderRadius: 8,
    borderWidth: 1,
    color: "#8D210F",
    marginTop: 14,
    padding: 12,
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
});
