import { useCallback, useEffect, useMemo, useState } from "react";
import {
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

import { DEMO_USER_ID, createLog, getLogs, getWeeklyReport } from "./src/api/client";
import type { LogEntry, LogResponse, WeeklyReport } from "./src/api/client";
import { HomeScreen } from "./src/screens/HomeScreen";
import { LogScreen } from "./src/screens/LogScreen";
import { ReportScreen } from "./src/screens/ReportScreen";

type ScreenName = "home" | "log" | "report";

const tabs: Array<{ key: ScreenName; label: string }> = [
  { key: "home", label: "Home" },
  { key: "log", label: "Log" },
  { key: "report", label: "Report" },
];

export default function App() {
  const [activeScreen, setActiveScreen] = useState<ScreenName>("home");
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [weeklyReport, setWeeklyReport] = useState<WeeklyReport | null>(null);
  const [lastLogResult, setLastLogResult] = useState<LogResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const currentBattery = useMemo(() => {
    if (logs.length > 0) {
      return logs[logs.length - 1].battery_after;
    }

    if (lastLogResult) {
      return lastLogResult.battery_after;
    }

    return weeklyReport?.average_battery ?? 50;
  }, [lastLogResult, logs, weeklyReport]);

  const refreshData = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [nextLogs, nextReport] = await Promise.all([
        getLogs(DEMO_USER_ID),
        getWeeklyReport(DEMO_USER_ID),
      ]);

      setLogs(nextLogs);
      setWeeklyReport(nextReport);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to load Battry data.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshData();
  }, [refreshData]);

  const handleSubmitLog = async (text: string) => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const result = await createLog({
        user_id: DEMO_USER_ID,
        text,
        logged_at: new Date().toISOString(),
      });

      setLastLogResult(result);
      await refreshData();
      setActiveScreen("home");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to submit log.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" />
      <View style={styles.shell}>
        <View style={styles.header}>
          <Text style={styles.appName}>Battry</Text>
          <Text style={styles.userLabel}>{DEMO_USER_ID}</Text>
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
