declare const process:
  | {
      env?: {
        EXPO_PUBLIC_API_URL?: string;
      };
    }
  | undefined;

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export const API_BASE_URL =
  typeof process !== "undefined" && process.env?.EXPO_PUBLIC_API_URL
    ? process.env.EXPO_PUBLIC_API_URL
    : DEFAULT_API_BASE_URL;

export type ParsedTask = {
  label: string;
  direction: "up" | "down";
};

export type CreateLogRequest = {
  text: string;
  logged_at: string;
};

export type LogResponse = {
  log_id: string;
  parsed_tasks: ParsedTask[];
  battery_before: number;
  battery_after: number;
};

export type LogEntry = LogResponse & {
  user_id: string;
  text: string;
  normalized_text: string;
  logged_at: string;
};

export type WeeklyReport = {
  user_id: string;
  log_count: number;
  average_battery: number;
  min_battery: number;
  max_battery: number;
  top_drainer: string | null;
  top_recharger: string | null;
  risk: "low" | "medium" | "high" | string;
};

type RequestOptions = {
  accessToken?: string;
  body?: unknown;
  method?: "GET" | "POST";
  query?: Record<string, string | number | boolean | null | undefined>;
};

function buildUrl(path: string, query?: RequestOptions["query"]) {
  const url = new URL(path, API_BASE_URL);

  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      url.searchParams.set(key, String(value));
    }
  });

  return url.toString();
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    Accept: "application/json",
    "Content-Type": "application/json",
  };

  if (options.accessToken) {
    headers.Authorization = `Bearer ${options.accessToken}`;
  }

  const response = await fetch(buildUrl(path, options.query), {
    body: options.body ? JSON.stringify(options.body) : undefined,
    headers,
    method: options.method ?? "GET",
  });

  const responseText = await response.text();
  const data = responseText ? JSON.parse(responseText) : null;

  if (!response.ok) {
    const detail =
      data && typeof data === "object" && "detail" in data ? String(data.detail) : null;
    throw new Error(detail ?? `Request failed with status ${response.status}`);
  }

  return data as T;
}

export function createLog(payload: CreateLogRequest, accessToken: string) {
  return request<LogResponse>("/logs", {
    accessToken,
    body: payload,
    method: "POST",
  });
}

export function getLogs(accessToken: string) {
  return request<LogEntry[]>("/logs", {
    accessToken,
  });
}

export function getWeeklyReport(accessToken: string) {
  return request<WeeklyReport>("/report/weekly", {
    accessToken,
  });
}
