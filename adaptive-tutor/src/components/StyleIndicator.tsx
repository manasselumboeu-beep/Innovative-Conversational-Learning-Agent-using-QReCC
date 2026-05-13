"use client";

interface Props {
  style: "foundation" | "standard" | "expert";
  proficiency: number;
}

const STYLE_CONFIG = {
  foundation: {
    label: "Foundation",
    color: "bg-amber-100 text-amber-800 border-amber-200",
    icon: "◆",
    desc: "Simplified explanations",
  },
  standard: {
    label: "Standard",
    color: "bg-blue-100 text-blue-800 border-blue-200",
    icon: "◈",
    desc: "Balanced depth",
  },
  expert: {
    label: "Expert",
    color: "bg-violet-100 text-violet-800 border-violet-200",
    icon: "◉",
    desc: "Technical depth",
  },
};

export function StyleIndicator({ style, proficiency }: Props) {
  const config = STYLE_CONFIG[style];
  const pct = Math.round(proficiency * 100);

  return (
    <div className="flex items-center gap-3">
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${config.color}`}
      >
        <span>{config.icon}</span>
        {config.label}
      </span>
      <div className="flex items-center gap-1.5 text-xs text-gray-400">
        <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-amber-400 via-blue-500 to-violet-500 rounded-full transition-all duration-500"
            style={{ width: `${pct}%` }}
          />
        </div>
        <span>{pct}%</span>
      </div>
    </div>
  );
}
