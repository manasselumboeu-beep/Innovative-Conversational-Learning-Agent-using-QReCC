"use client";

interface Props {
  type: string;
  show: boolean;
}

const TYPE_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  repetition: {
    label: "Repetition",
    color: "bg-orange-100 text-orange-700 border-orange-200",
    icon: "↺",
  },
  vague: {
    label: "Vague",
    color: "bg-yellow-100 text-yellow-700 border-yellow-200",
    icon: "?",
  },
  contradiction: {
    label: "Contradiction",
    color: "bg-red-100 text-red-700 border-red-200",
    icon: "⚡",
  },
  scope: {
    label: "Scope Shift",
    color: "bg-purple-100 text-purple-700 border-purple-200",
    icon: "→",
  },
};

export function ConfusionBadge({ type, show }: Props) {
  if (!show || type === "none" || !TYPE_CONFIG[type]) return null;

  const config = TYPE_CONFIG[type];

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium border ${config.color} animate-pulse`}
      title="Confusion detected — handling before answering"
    >
      <span className="font-bold">{config.icon}</span>
      {config.label} detected
    </span>
  );
}
