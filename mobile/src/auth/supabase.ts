import "react-native-url-polyfill/auto";

import AsyncStorage from "@react-native-async-storage/async-storage";
import { createClient } from "@supabase/supabase-js";
import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";

declare const process:
  | {
      env?: {
        EXPO_PUBLIC_SUPABASE_ANON_KEY?: string;
        EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY?: string;
        EXPO_PUBLIC_SUPABASE_URL?: string;
      };
    }
  | undefined;

const supabaseUrl =
  typeof process !== "undefined" ? process.env?.EXPO_PUBLIC_SUPABASE_URL ?? "" : "";
const supabaseKey =
  typeof process !== "undefined"
    ? process.env?.EXPO_PUBLIC_SUPABASE_ANON_KEY ??
      process.env?.EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY ??
      ""
    : "";

// Screens use this to show a clear setup message instead of failing silently.
export const isSupabaseAuthConfigured = Boolean(supabaseUrl && supabaseKey);

// Supabase Auth needs a storage adapter. Native apps should not keep tokens in
// plain AsyncStorage, so iOS/Android use Expo SecureStore instead.
const nativeSecureStorage = {
  getItem: (key: string) => SecureStore.getItemAsync(key),
  removeItem: (key: string) => SecureStore.deleteItemAsync(key),
  setItem: (key: string, value: string) => SecureStore.setItemAsync(key, value),
};

export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    // Supabase can refresh the mobile session for us while the app is active.
    autoRefreshToken: true,
    // React Native does not complete auth through browser URL callbacks here.
    detectSessionInUrl: false,
    persistSession: true,
    // Web builds cannot use SecureStore, so they fall back to AsyncStorage.
    storage: Platform.OS === "web" ? AsyncStorage : nativeSecureStorage,
  },
});
