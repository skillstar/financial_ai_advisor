import { AnalysisResult, ApiResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const analyzeData = async (
  file: File,
  query: string,
): Promise<ApiResponse<AnalysisResult>> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('query', query);

  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      return {
        success: false,
        error: errorData.detail || '分析请求失败',
      };
    }

    const data = await response.json();
    return {
      success: true,
      data,
    };
  } catch (error) {
    console.error('API Error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : '未知错误',
    };
  }
};
