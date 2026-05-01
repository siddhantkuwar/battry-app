import { useCallback, useEffect, useMemo, useState } from "react";
import {
  AppState,
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import type { Session } from "@supabase/supabase-js";

import { createLog, getLogs, getWeeklyReport } from "./src/api/client";
import type { LogEntry, LogResponse, WeeklyReport } from "./src/api/client";
import { supabase } from "./src/auth/supabase";
import { AuthScreen } from "./src/screens/AuthScreen";
import { HomeScreen } from "./src/screens/HomeScreen";
import { LogScreen } from "./src/screens/LogScreen";
import { ReportScreen } from "./src/screens/ReportScreen";

const DEFAULT_BATTERY = 50;

type ScreenName = "home" | "log" | "report";

type TabDefinition = {
  key: ScreenName;
  label: string;
};

// The app uses a tiny hand-rolled tab switcher for now. Keeping tab metadata in
// one list prevents the tab bar and screen names from drifting apart.
const tabs: TabDefinition[] = [
  { key: "home", label: "Home" },
  { key: "log", label: "Log" },
  { key: "report", label: "Report" },
];

function getReadableErrorMessage(error: unknown, fallback: string) {
  // Fetch and Supabase errors normally arrive as Error objects. The fallback
  // covers unexpected values without crashing the UI.
  return error instanceof Error ? error.message : fallback;
}

function getCurrentBattery({
  lastLogResult,
  logs,
  weeklyReport,
}: {
  lastLogResult: LogResponse | null;
  logs: LogEntry[];
  weeklyReport: WeeklyReport | null;
}) {
  // The freshest exact score is the newest saved log. Immediately after submit,
  // lastLogResult lets the UI update before the refresh request finishes.
  if (logs.length > 0) {
    return logs[logs.length - 1].battery_after;
  }

  if (lastLogResult) {
    return lastLogResult.battery_after;
  }

  return weeklyReport?.average_battery ?? DEFAULT_BATTERY;
}

export default function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const [activeScreen, setActiveScreen] = useState<ScreenName>("home");
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [weeklyReport, setWeeklyReport] = useState<WeeklyReport | null>(null);
  const [lastLogResult, setLastLogResult] = useState<LogResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const currentBattery = useMemo(
    () => getCurrentBattery({ lastLogResult, logs, weeklyReport }),
    [lastLogResult, logs, weeklyReport],
  );

  useEffect(() => {
    // On app launch, ask Supabase whether a previous session was saved.
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setIsAuthLoading(false);
    });

    // Supabase emits auth changes for sign in, sign up, refresh, and sign out.
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      if (!nextSession) {
        // Clear user-specific data immediately when the user signs out.
        setLogs([]);
        setWeeklyReport(null);
        setLastLogResult(null);
      }
    });

    // Mobile apps can be backgrounded for a long time. Starting/stopping token
    // refresh with app state avoids unnecessary refresh work in the background.
    const appStateSubscription = AppState.addEventListener("change", (state) => {
      if (state === "active") {
        supabase.auth.startAutoRefresh();
      } else {
        supabase.auth.stopAutoRefresh();
      }
    });

    return () => {
      subscription.unsubscribe();
      appStateSubscription.remove();
    };
  }, []);

  const refreshData = useCallback(async () => {
    if (!session?.access_token) {
      return;
    }

    // One refresh updates both the timeline and the weekly report so screens
    // stay consistent after a submit or manual refresh.
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [nextLogs, nextReport] = await Promise.all([
        getLogs(session.access_token),
        getWeeklyReport(session.access_token),
      ]);

      setLogs(nextLogs);
      setWeeklyReport(nextReport);
    } catch (error) {
      setErrorMessage(getReadableErrorMessage(error, "Unable to load Battry data."));
    } finally {
      setIsLoading(false);
    }
  }, [session?.access_token]);

  useEffect(() => {
    // Load data as soon as a valid session appears.
    if (session?.access_token) {
      void refreshData();
    }
  }, [refreshData, session?.access_token]);

  const handleSubmitLog = async (text: string) => {
    if (!session?.access_token) {
      setErrorMessage("Sign in before submitting a log.");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const result = await createLog(
        {
          text,
          logged_at: new Date().toISOString(),
        },
        session.access_token,
      );

      setLastLogResult(result);
      await refreshData();
      setActiveScreen("home");
    } catch (error) {
      setErrorMessage(getReadableErrorMessage(error, "Unable to submit log."));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignOut = async () => {
    // Supabase will trigger onAuthStateChange, which clears app state above.
    await supabase.auth.signOut();
  };

  if (isAuthLoading) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.loadingShell}>
          <Text style={styles.loadingText}>Loading Battry</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!session) {
    return <AuthScreen />;
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" />
      <View style={styles.shell}>
        <View style={styles.header}>
          <Text style={styles.appName}>Battry</Text>
          <TouchableOpacity accessibilityRole="button" onPress={handleSignOut}>
            <Text style={styles.userLabel}>{session.user.email ?? "Sign out"}</Text>
          </TouchableOpacity>
        </View>

        {errorMessage ? <Text style={styles.error}>{errorMessage}</Text> : null}

        <View style={styles.content}>
          {activeScreen === "home" ? (
            <HomeScreen
              currentBattery={currentBattery}
              isLoading={isLoading}
              lastLogResult={lastLogResult}
              recentLogs={logs.slice(-3).reverse()}
              weeklyReport={weeklyReport}
              onRefresh={refreshData}
            />
          ) : null}

          {activeScreen === "log" ? (
            <LogScreen
              isSubmitting={isLoading}
              lastLogResult={lastLogResult}
              onSubmit={handleSubmitLog}
            />
          ) : null}

          {activeScreen === "report" ? (
            <ReportScreen
              isLoading={isLoading}
              logs={logs}
              report={weeklyReport}
              onRefresh={refreshData}
            />
          ) : null}
        </View>

        <View style={styles.tabBar}>
          {tabs.map((tab) => (
            <TouchableOpacity
              key={tab.key}
              accessibilityRole="button"
              style={[styles.tab, activeScreen === tab.key ? styles.activeTab : null]}
              onPress={() => setActiveScreen(tab.key)}
            >
              <Text style={[styles.tabText, activeScreen === tab.key ? styles.activeTabText : null]}>
                {tab.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#F7F7F2",
  },
  shell: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 12,
  },
  loadingShell: {
    alignItems: "center",
    flex: 1,
    justifyContent: "center",
    padding: 20,
  },
  loadingText: {
    color: "#151515",
    fontSize: 18,
    fontWeight: "800",
  },
  header: {
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-between",
    paddingBottom: 16,
  },
  appName: {
    color: "#151515",
    fontSize: 28,
    fontWeight: "800",
  },
  userLabel: {
    color: "#6F706B",
    fontSize: 13,
    fontWeight: "600",
  },
  error: {
    backgroundColor: "#FFE8E2",
    borderColor: "#D9482F",
    borderRadius: 8,
    borderWidth: 1,
    color: "#8D210F",
    marginBottom: 12,
    padding: 12,
  },
  content: {
    flex: 1,
  },
  tabBar: {
    backgroundColor: "#FFFFFF",
    borderColor: "#DADBD2",
    borderRadius: 8,
    borderWidth: 1,
    flexDirection: "row",
    gap: 8,
    marginBottom: 12,
    padding: 6,
  },
  tab: {
    alignItems: "center",
    borderRadius: 6,
    flex: 1,
    paddingVertical: 10,
  },
  activeTab: {
    backgroundColor: "#151515",
  },
  tabText: {
    color: "#6F706B",
    fontSize: 14,
    fontWeight: "700",
  },
  activeTabText: {
    color: "#FFFFFF",
  },
});
