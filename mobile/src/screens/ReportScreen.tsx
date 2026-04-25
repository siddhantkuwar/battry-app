import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";

import type { LogEntry, WeeklyReport } from "../api/client";

type ReportScreenProps = {
  isLoading: boolean;
  logs: LogEntry[];
  report: WeeklyReport | null;
  onRefresh: () => void;
};

export function ReportScreen({ isLoading, logs, report, onRefresh }: ReportScreenProps) {
  return (
    <ScrollView contentContainerStyle={styles.screen}>
      <View style={styles.row}>
        <Text style={styles.title}>Weekly report</Text>
        <TouchableOpacity accessibilityRole="button" onPress={onRefresh}>
          <Text style={styles.action}>{isLoading ? "Loading" : "Refresh"}</Text>
        </TouchableOpacity>
      </View>

      {report ? (
        <>
          <View style={styles.statsGrid}>
            <Stat label="Average" value={`${report.average_battery}%`} />
            <Stat label="Min" value={`${report.min_battery}%`} />
            <Stat label="Max" value={`${report.max_battery}%`} />
            <Stat label="Risk" value={report.risk} />
          </View>

          <View style={styles.panel}>
            <Text style={styles.sectionTitle}>Insight signals</Text>
            <View style={styles.signalRow}>
              <Text style={styles.signalLabel}>Top drainer</Text>
              <Text style={styles.signalValue}>{report.top_drainer ?? "None yet"}</Text>
            </View>
            <View style={styles.signalRow}>
              <Text style={styles.signalLabel}>Top recharger</Text>
              <Text style={styles.signalValue}>{report.top_recharger ?? "None yet"}</Text>
            </View>
          </View>
        </>
      ) : (
        <View style={styles.panel}>
          <Text style={styles.empty}>No report data yet.</Text>
        </View>
      )}

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>Day list</Text>
        {logs.length > 0 ? (
          logs
            .slice()
            .reverse()
            .map((log) => (
              <View key={log.log_id} style={styles.logRow}>
                <View style={styles.logCopy}>
                  <Text style={styles.logDate}>{new Date(log.logged_at).toLocaleDateString()}</Text>
                  <Text style={styles.logText} numberOfLines={2}>
                    {log.text}
                  </Text>
                </View>
                <Text style={styles.logBattery}>{log.battery_after}%</Text>
              </View>
            ))
        ) : (
          <Text style={styles.empty}>Submit a log to build the timeline.</Text>
        )}
      </View>
    </ScrollView>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.stat}>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    gap: 14,
    paddingBottom: 16,
  },
  row: {
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-between",
  },
  title: {
    color: "#151515",
    fontSize: 24,
    fontWeight: "900",
  },
  action: {
    color: "#2C6E49",
    fontSize: 14,
    fontWeight: "800",
  },
  statsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  stat: {
    backgroundColor: "#FFFFFF",
    borderColor: "#DADBD2",
    borderRadius: 8,
    borderWidth: 1,
    flexBasis: "48%",
    flexGrow: 1,
    padding: 14,
  },
  statLabel: {
    color: "#6F706B",
    fontSize: 12,
    fontWeight: "800",
    textTransform: "uppercase",
  },
  statValue: {
    color: "#151515",
    fontSize: 26,
    fontWeight: "900",
    marginTop: 8,
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
  signalRow: {
    borderTopColor: "#ECEDE7",
    borderTopWidth: 1,
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 12,
    paddingTop: 12,
  },
  signalLabel: {
    color: "#6F706B",
    fontSize: 14,
    fontWeight: "700",
  },
  signalValue: {
    color: "#151515",
    fontSize: 14,
    fontWeight: "900",
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
  logCopy: {
    flex: 1,
  },
  logDate: {
    color: "#6F706B",
    fontSize: 12,
    fontWeight: "800",
    marginBottom: 4,
  },
  logText: {
    color: "#33342F",
    fontSize: 14,
    lineHeight: 20,
  },
  logBattery: {
    color: "#151515",
    fontSize: 16,
    fontWeight: "900",
  },
  empty: {
    color: "#6F706B",
    fontSize: 14,
    lineHeight: 20,
  },
});
