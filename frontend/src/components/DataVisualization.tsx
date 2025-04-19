import React from 'react';
import { Card, Tabs, Typography, Empty, Spin, Flex } from 'antd';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title as ChartTitle,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions,
} from 'chart.js';
import { Line, Bar, Pie, Scatter } from 'react-chartjs-2';
import { ChartData as AppChartData } from '../types';

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  ChartTitle,
  Tooltip,
  Legend,
);

const { Title, Paragraph } = Typography;

interface DataVisualizationProps {
  charts: AppChartData[];
  analysis: string;
  loading: boolean;
}

const DataVisualization: React.FC<DataVisualizationProps> = ({ charts, analysis, loading }) => {
  // 为每种图表类型创建配置
  const createChartConfig = (
    chart: AppChartData,
  ): {
    data: any;
    options: any;
  } => {
    const defaultOptions = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: chart.title,
        },
      },
    };

    // 如果有预定义的图表数据，直接返回
    if (chart.data) {
      return {
        data: chart.data,
        options: defaultOptions,
      };
    }

    // 否则返回空数据
    return {
      data: {
        labels: [],
        datasets: [],
      },
      options: defaultOptions,
    };
  };

  const renderChart = (chart: AppChartData) => {
    if (chart.image) {
      return <img src={chart.image} alt={chart.title} className="w-full" />;
    }

    const { data, options } = createChartConfig(chart);

    // 为每种图表类型单独渲染，避免类型错误
    switch (chart.type) {
      case 'line':
        return <Line data={data} options={options} />;
      case 'bar':
        return <Bar data={data} options={options} />;
      case 'pie':
        return <Pie data={data} options={options} />;
      case 'scatter':
        return <Scatter data={data} options={options} />;
      default:
        return <Empty description="不支持的图表类型" />;
    }
  };

  if (loading) {
    return (
      <Card className="text-center p-10">
        <Flex vertical align="center" gap="middle">
          <Spin size="large" />
          <Title level={4}>正在分析数据并生成可视化...</Title>
        </Flex>
      </Card>
    );
  }

  if (charts.length === 0) {
    return (
      <Card>
        <Empty description="尚无可视化数据" />
      </Card>
    );
  }

  return (
    <Card>
      <Title level={4}>数据分析结果</Title>

      <Paragraph className="whitespace-pre-line mb-5">{analysis}</Paragraph>

      <Tabs defaultActiveKey="0" type="card">
        {charts.map((chart, index) => (
          <Tabs.TabPane tab={chart.title} key={index.toString()}>
            <div className="h-[400px] relative">{renderChart(chart)}</div>
            <Paragraph className="mt-4">{chart.description}</Paragraph>
          </Tabs.TabPane>
        ))}
      </Tabs>
    </Card>
  );
};

export default DataVisualization;
