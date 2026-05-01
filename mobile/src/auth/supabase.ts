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

export const isSupabaseAuthConfigured = Boolean(supabaseUrl && supabaseKey);

const nativeSecureStorage = {
  getItem: (key: string) => SecureStore.getItemAsync(key),
  removeItem: (key: string) => SecureStore.deleteItemAsync(key),
  setItem: (key: string, value: string) => SecureStore.setItemAsync(key, value),
};

export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    autoRefreshToken: true,
    detectSessionInUrl: false,
    persistSession: true,
    storage: Platform.OS === "web" ? AsyncStorage : nativeSecureStorage,
  },
});
