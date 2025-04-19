export type ChartData = {
  id: string;
  title: string;
  type: 'bar' | 'line' | 'pie' | 'doughnut' | 'scatter';
  description: string;
  data: {
    labels?: string[];
    datasets: Array<{
      label: string;
      data: number[] | Array<{ x: number; y: number }>;
      backgroundColor?: string | string[];
      borderColor?: string | string[];
      tension?: number;
      [key: string]: any;
    }>;
  };
};

export type AnalysisResult = {
  analysis: string;
  charts: ChartData[];
  strategy: string;
};

export type ApiResponse<T> = {
  success: boolean;
  data?: T;
  error?: string;
};

// 消息类型
export type Message = {
  id: string;
  type: 'user' | 'bot' | 'file';
  role?: 'bot' | 'analyst' | 'strategist' | 'error' | 'user' | 'file'; // 添加可选的 role 属性
  content: string | any; // 可以是字符串或复杂对象
};

export interface CustomFile extends File {
  path?: string;
  uploaded?: boolean;
}
