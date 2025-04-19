// src/hooks/useWebSocketAnalysis.ts
import { useState, useEffect, useCallback, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { useAtom } from 'jotai';
import { messagesAtom, loadingAtom } from '../states/atoms';
import { ChartData, CustomFile, Message } from '../types'; // 导入共享类型

// 进度数据类型
export interface ProgressData {
  stage: string;
  message: string;
  data?: {
    analysis?: string;
    charts?: ChartData[];
    strategy?: string;
  };
}

// WebSocket消息类型
interface WebSocketMessage {
  type: 'start' | 'progress' | 'result' | 'error' | 'cancelled';
  message?: string;
  data?: any;
}

const stageToMessage: Record<string, string> = {
  start: '正在启动分析...',
  agent_created: '分析专家已就绪...',
  analysis_started: '正在分析数据...',
  analysis_completed: '数据分析完成，生成策略中...',
  strategy_started: '正在制定策略建议...',
  completed: '分析与策略生成完成',
  error: '分析过程中出现错误',
  fallback: '使用备用分析方法...',
};

export const useWebSocketAnalysis = () => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [clientId] = useState<string>(() => uuidv4());
  const [connected, setConnected] = useState<boolean>(false);
  const [messages, setMessages] = useAtom(messagesAtom);
  const [loading, setLoading] = useAtom(loadingAtom);
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef<number>(0);
  const MAX_RECONNECT_ATTEMPTS = 5;

  // 连接WebSocket
  const connectWebSocket = useCallback(() => {
    console.log('===== 开始连接WebSocket =====');
    try {
      // 两种方式都可以测试：

      // 方法1: 通过代理连接（推荐）
      const wsUrl = `/ws/analysis/${clientId}`;
      const fullWsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}${wsUrl}`;

      // 方法2: 直接连接
      // const fullWsUrl = `ws://localhost:8000/ws/analysis/${clientId}`;

      console.log('尝试连接到:', fullWsUrl);

      // 创建新的WebSocket连接
      console.log('正在创建WebSocket实例...');
      const newSocket = new WebSocket(fullWsUrl);
      console.log('WebSocket实例已创建');

      // 设置事件处理器
      newSocket.onopen = event => {
        console.log('WebSocket连接成功!', event);
        setConnected(true);
        reconnectAttempts.current = 0;
      };

      newSocket.onclose = event => {
        console.log(`WebSocket disconnected (Code: ${event.code})`);
        setConnected(false);

        // 尝试重连（如果不是正常关闭）
        if (event.code !== 1000 && reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts.current += 1;
          const reconnectDelay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);

          console.log(
            `Attempting to reconnect in ${reconnectDelay / 1000}s (attempt ${reconnectAttempts.current})`,
          );

          if (reconnectTimer.current) {
            clearTimeout(reconnectTimer.current);
          }

          reconnectTimer.current = setTimeout(() => {
            connectWebSocket();
          }, reconnectDelay);
        }
      };

      newSocket.onerror = error => {
        console.error('WebSocket error:', error);
      };

      newSocket.onmessage = event => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          handleSocketMessage(data);
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };

      setSocket(newSocket);

      return () => {
        if (newSocket && newSocket.readyState === WebSocket.OPEN) {
          newSocket.close();
        }
      };
    } catch (err) {
      console.error('Error connecting to WebSocket:', err);
    }
  }, [clientId]);

  // 初始化WebSocket连接
  useEffect(() => {
    connectWebSocket();

    return () => {
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }

      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, [connectWebSocket]);

  // 处理WebSocket消息
  const handleSocketMessage = useCallback(
    (data: WebSocketMessage) => {
      const { type } = data;
      console.log('收到WebSocket消息:', type, data);

      switch (type) {
        case 'start':
          setLoading(true);
          setProgress(null);

          // 添加开始消息
          setMessages(prevMessages => [
            ...prevMessages,
            {
              id: uuidv4(),
              type: 'bot',
              role: 'bot',
              content: '开始分析数据...',
            } as Message,
          ]);
          break;

        case 'progress':
          if (data.data) {
            setProgress(data.data);

            // 添加文本进度消息
            setMessages(prevMessages => [
              ...prevMessages,
              {
                id: uuidv4(),
                type: 'bot',
                content: data.data.message,
              },
            ]);

            // 检查completed阶段的最终结果
            if (data.data.stage === 'completed' && data.data.data) {
              const resultData = data.data.data;

              // 添加分析结果
              if (resultData.analysis) {
                setMessages(prevMessages => [
                  ...prevMessages,
                  {
                    id: uuidv4(),
                    type: 'bot',
                    role: 'analyst',
                    content: {
                      analysis: resultData.analysis,
                      charts: resultData.charts || [],
                    },
                  },
                ]);
              }

              // 添加策略结果
              if (resultData.strategy) {
                setMessages(prevMessages => [
                  ...prevMessages,
                  {
                    id: uuidv4(),
                    type: 'bot',
                    role: 'strategist',
                    content: {
                      strategy: resultData.strategy,
                    },
                  },
                ]);
              }
            }
          }
          break;

        case 'result':
          setLoading(false);

          // 添加策略师消息
          if (data.data && data.data.strategy) {
            setMessages(prevMessages => [
              ...prevMessages,
              {
                id: uuidv4(),
                type: 'bot',
                role: 'strategist',
                content: {
                  strategy: data.data.strategy,
                },
              } as Message,
            ]);
          }
          break;

        case 'error':
          setLoading(false);

          // 添加错误消息
          setMessages(prevMessages => [
            ...prevMessages,
            {
              id: uuidv4(),
              type: 'bot',
              role: 'error',
              content: `分析出错: ${data.message || '未知错误'}`,
            } as Message,
          ]);
          break;

        case 'cancelled':
          setLoading(false);
          break;

        default:
          console.log('Unknown message type:', type);
      }
    },
    [setLoading, setMessages, setProgress],
  );

  // 发送分析请求 - 使用CustomFile类型
  const runAnalysis = useCallback(
    (file: CustomFile, query: string) => {
      if (!socket || socket.readyState !== WebSocket.OPEN || !file) {
        console.error('WebSocket not connected or file missing');
        return false;
      }

      // 添加用户消息
      const messageId = uuidv4();
      setMessages(prevMessages => [
        ...prevMessages,
        {
          id: messageId,
          type: 'user',
          content: query,
        } as Message,
      ]);

      try {
        // 使用file.path如果存在，否则使用默认路径
        const filePath = file.path || `/uploads/${file.name}`;

        // 发送请求
        socket.send(
          JSON.stringify({
            file_path: filePath,
            query,
          }),
        );

        setLoading(true);
        return true;
      } catch (err) {
        console.error('Error sending analysis request:', err);
        return false;
      }
    },
    [socket, setMessages, setLoading],
  );

  return {
    runAnalysis,
    connected,
    loading,
    progress,
    reconnect: connectWebSocket,
  };
};
