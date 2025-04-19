import { useCallback } from 'react';
import { ChartData as ChartJsData, ChartOptions } from 'chart.js';
import { ChartData } from '../types';

export const useChartConfig = () => {
  const getChartJsConfig = useCallback(
    (
      chart: ChartData,
    ): {
      data: ChartJsData;
      options: ChartOptions;
    } => {
      // 默认配置
      const defaultOptions: ChartOptions = {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: chart.title,
          },
          tooltip: {
            enabled: true,
          },
        },
      };

      // 如果图表包含预定义的数据，直接返回
      if (chart.data) {
        return {
          data: chart.data,
          options: defaultOptions,
        };
      }

      // 否则返回空数据模板（实际应用中不应该走到这里）
      return {
        data: {
          labels: [],
          datasets: [],
        },
        options: defaultOptions,
      };
    },
    [],
  );

  return { getChartJsConfig };
};
