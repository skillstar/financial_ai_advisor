// hooks/useAnalysisApi.ts
import { useAtom } from 'jotai';
import { messagesAtom, loadingAtom } from '../states/atoms';
import { v4 as uuidv4 } from 'uuid';
import { analyzeData } from '../services/api';

export const useAnalysisApi = () => {
  const [messages, setMessages] = useAtom(messagesAtom);
  const [loading, setLoading] = useAtom(loadingAtom);

  const runAnalysis = async (file: File, query: string) => {
    if (!file || !query.trim()) return;

    // 添加用户消息
    const userMessage = {
      id: uuidv4(),
      type: 'user',
      content: query,
    };
    setMessages(prev => [...prev, userMessage]);

    // 设置加载状态
    setLoading(true);

    try {
      // 使用API服务发送请求
      const response = await analyzeData(file, query);

      if (!response.success) {
        // 处理API错误
        throw new Error(response.error || 'API请求失败');
      }

      // 创建机器人回复消息
      const botMessage = {
        id: uuidv4(),
        type: 'bot',
        content: response.data, // 直接传递结果数据
      };

      // 更新消息
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Analysis error:', error);

      // 添加错误消息
      const errorMessage = {
        id: uuidv4(),
        type: 'bot',
        content: `分析过程中出现错误: ${error instanceof Error ? error.message : '未知错误'}`,
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return { runAnalysis };
};
