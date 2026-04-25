import { Text, TouchableOpacity, View, StyleSheet } from "react-native";

import type { LogEntry, LogResponse, WeeklyReport } from "../api/client";

type HomeScreenProps = {
  currentBattery: number;
  isLoading: boolean;
  lastLogResult: LogResponse | null;
  recentLogs: LogEntry[];
  weeklyReport: WeeklyReport | null;
  onRefresh: () => void;
};

export function HomeScreen({
  currentBattery,
  isLoading,
  lastLogResult,
  recentLogs,
  weeklyReport,
  onRefresh,
}: HomeScreenProps) {
  return (
    <View style={styles.screen}>
      <View style={styles.batteryPanel}>
        <Text style={styles.label}>Current battery</Text>
        <Text style={styles.batteryValue}>{Math.round(currentBattery)}%</Text>
        <View style={styles.track}>
          <View style={[styles.fill, { width: `${Math.max(0, Math.min(100, currentBattery))}%` }]} />
        </View>
        <Text style={styles.risk}>Risk: {weeklyReport?.risk ?? "not enough data"}</Text>
      </View>

      {lastLogResult ? (
        <View style={styles.panel}>
          <Text style={styles.sectionTitle}>Latest change</Text>
          <Text style={styles.change}>
            {lastLogResult.battery_before}% to {lastLogResult.battery_after}%
          </Text>
          <Text style={styles.muted}>
            {lastLogResult.parsed_tasks.map((task) => task.label).join(", ") || "No labels found"}
          </Text>
        </View>
      ) : null}

      <View style={styles.panel}>
        <View style={styles.row}>
          <Text style={styles.sectionTitle}>Recent logs</Text>
          <TouchableOpacity accessibilityRole="button" onPress={onRefresh}>
            <Text style={styles.action}>{isLoading ? "Loading" : "Refresh"}</Text>
          </TouchableOpacity>
        </View>

        {recentLogs.length > 0 ? (
          recentLogs.map((log) => (
            <View key={log.log_id} style={styles.logRow}>
              <Text style={styles.logText} numberOfLines={2}>
                {log.text}
              </Text>
              <Text style={styles.logBattery}>{log.battery_after}%</Text>
            </View>
          ))
        ) : (
          <Text style={styles.muted}>No logs yet.</Text>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    gap: 14,
  },
  batteryPanel: {
    backgroundColor: "#FFFFFF",
    borderColor: "#DADBD2",
    borderRadius: 8,
    borderWidth: 1,
    padding: 18,
  },
  label: {
    color: "#6F706B",
    fontSize: 13,
    fontWeight: "700",
    textTransform: "uppercase",
  },
  batteryValue: {
    color: "#151515",
    fontSize: 56,
    fontWeight: "900",
    marginTop: 6,
  },
  track: {
    backgroundColor: "#E5E6DE",
    borderRadius: 6,
    height: 12,
    marginTop: 8,
    overflow: "hidden",
  },
  fill: {
    backgroundColor: "#55A36A",
    height: "100%",
  },
  risk: {
    color: "#4F514C",
    fontSize: 15,
    fontWeight: "700",
    marginTop: 12,
    textTransform: "capitalize",
  },
  panel: {
    backgroundColor: "#FFFFFF",
    borderColor: "#DADBD2",
    borderRadius: 8,
    borderWidth: 1,
    padding: 16,
  },
  sectionTitle: {
    color: "#151515",
    fontSize: 18,
    fontWeight: "800",
  },
  change: {
    color: "#151515",
    fontSize: 28,
    fontWeight: "900",
    marginTop: 6,
  },
  muted: {
    color: "#6F706B",
    fontSize: 14,
    lineHeight: 20,
    marginTop: 6,
  },
  row: {
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-between",
  },
  action: {
    color: "#2C6E49",
    fontSize: 14,
    fontWeight: "800",
  },
  logRow: {
    alignItems: "center",
    borderTopColor: "#ECEDE7",
    borderTopWidth: 1,
    flexDirection: "row",
    gap: 12,
    justifyContent: "space-between",
    marginTop: 12,
    paddingTop: 12,
  },
  logText: {
    color: "#33342F",
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
  },
  logBattery: {
    color: "#151515",
    fontSize: 16,
    fontWeight: "900",
  },
});
