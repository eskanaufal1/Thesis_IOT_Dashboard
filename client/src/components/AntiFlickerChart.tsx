import { useEffect, useRef, useCallback, useMemo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  LineController,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend
);

interface AntiFlickerChartProps {
  data: Array<{ timestamp: number; value: number }>;
  color: string;
  title: string;
  unit: string;
}

export const AntiFlickerChart = ({
  data,
  color,
  title,
  unit,
}: AntiFlickerChartProps) => {
  const chartRef = useRef<ChartJS<"line"> | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const isInitialized = useRef(false);

  // Color mapping
  const colorMap = useMemo(() => ({
    blue: "#3B82F6",
    green: "#10B981",
    red: "#EF4444",
    purple: "#8B5CF6",
    indigo: "#6366F1",
    pink: "#EC4899",
    teal: "#14B8A6",
  }), []);

  const getColor = useCallback((colorKey: string) =>
    colorMap[colorKey as keyof typeof colorMap] || "#3B82F6", [colorMap]);

  useEffect(() => {
    if (!canvasRef.current || isInitialized.current) return;

    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    // Destroy any existing chart
    const existingChart = ChartJS.getChart(canvasRef.current);
    if (existingChart) {
      existingChart.destroy();
    }

    const chartColor = getColor(color);

    // Create initial dataset with actual timestamps for real-time scrolling
    const formatTime = (timestamp: number) => {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false, // Use 24-hour format for consistency
      });
    };

    const initialLabels = data
      .slice(-20)
      .map((point) => formatTime(point.timestamp));
    const initialData = data
      .slice(-20)
      .map((point) => Number(point.value.toFixed(1)));

    chartRef.current = new ChartJS(ctx, {
      type: "line",
      data: {
        labels: initialLabels,
        datasets: [
          {
            label: title,
            data: initialData,
            borderColor: chartColor,
            backgroundColor: "transparent",
            borderWidth: 2,
            fill: false,
            tension: 0.2,
            pointRadius: 1, // Small visible points for better interaction
            pointHoverRadius: 6,
            pointBackgroundColor: chartColor,
            pointBorderColor: chartColor, // Use chart color instead of white
            pointBorderWidth: 1,
            pointHoverBackgroundColor: chartColor,
            pointHoverBorderColor: "#ffffff", // White border only on hover for contrast
            pointHoverBorderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        animations: {
          colors: false,
          x: false,
          y: false,
        },
        transitions: {
          active: {
            animation: {
              duration: 0,
            },
          },
        },
        interaction: {
          intersect: false,
          mode: "index",
          axis: "x",
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            backgroundColor: "rgba(255, 255, 255, 0.95)",
            titleColor: "#374151",
            bodyColor: "#374151",
            borderColor: "#E5E7EB",
            borderWidth: 1,
            animation: false,
            displayColors: false,
            callbacks: {
              title: (context) => {
                return `Time: ${context[0].label}`;
              },
              label: (context) => {
                const value = Number(context.parsed.y).toFixed(1);
                return `${title}: ${value} ${unit}`;
              },
            },
          },
        },
        scales: {
          x: {
            display: true,
            grid: {
              display: true,
              color: "rgba(156, 163, 175, 0.2)",
            },
            ticks: {
              color: "#6B7280",
              font: { size: 9 },
              maxTicksLimit: window.innerWidth < 768 ? 4 : 5, // Fewer ticks on mobile
              maxRotation: 0, // Keep labels horizontal
              minRotation: 0,
            },
            title: {
              display: false, // Remove x-axis title to save space
            },
          },
          y: {
            display: true,
            grid: {
              display: true,
              color: "rgba(156, 163, 175, 0.2)",
            },
            ticks: {
              color: "#6B7280",
              font: { size: 9 },
              maxTicksLimit: 6,
              callback: function (value) {
                return Number(value).toFixed(1) + unit;
              },
              padding: 5, // Reduce padding to give more space to chart
            },
            title: {
              display: true,
              text: `${title} (${unit})`,
              color: "#374151", // Darker color for better visibility
              font: {
                size: 11,
                weight: "bold", // Make it bolder for better visibility
              },
            },
          },
        },
        elements: {
          point: {
            radius: 1,
            hoverRadius: 6,
            borderWidth: 1,
            hoverBorderWidth: 2,
          },
          line: {
            borderWidth: 2,
            tension: 0.2,
          },
        },
      },
    });

    isInitialized.current = true;

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
      isInitialized.current = false;
    };
  }, []);

  // Update chart data when props change
  useEffect(() => {
    if (!chartRef.current || !isInitialized.current) return;

    const formatTime = (timestamp: number) => {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false, // Use 24-hour format for consistency
      });
    };

    const newData = data
      .slice(-20)
      .map((point) => Number(point.value.toFixed(1)));
    const newLabels = data
      .slice(-20)
      .map((point) => formatTime(point.timestamp));

    // Always update the chart data - don't rely on hash comparison for better reliability
    const dataset = chartRef.current.data.datasets[0];

    // Update all data points
    dataset.data = newData;

    // Update labels for real-time scrolling effect
    chartRef.current.data.labels = newLabels;

    try {
      chartRef.current.update("none");
    } catch (error) {
      console.warn("Chart update error:", error);
    }
  }, [data, title, color, unit, getColor]);

  const currentValue = data[data.length - 1]?.value || 0;

  return (
    <div className="space-y-4">
      {/* Header with current value */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Current: {currentValue.toFixed(1)} {unit}
        </span>
        <div className="flex items-center space-x-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: getColor(color) }}
          />
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {title}
          </span>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-64 w-full">
        <canvas ref={canvasRef} style={{ width: "100%", height: "100%" }} />
      </div>

      {/* Statistics */}
      <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
        <span>Data Points: 20</span>
        <span>Live updates • 1s interval</span>
      </div>
    </div>
  );
};
