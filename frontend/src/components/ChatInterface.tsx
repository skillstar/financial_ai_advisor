import React, { useRef, useState, useEffect } from 'react';
import { Bubble, Attachments } from '@ant-design/x';
import { Button, Card, Flex, Input, Upload, Space, Spin, Tooltip, message, Progress } from 'antd';
import {
  SendOutlined,
  UploadOutlined,
  UserOutlined,
  RobotOutlined,
  DeleteOutlined,
  VerticalAlignTopOutlined,
  VerticalAlignBottomOutlined,
} from '@ant-design/icons';
import { useAtom } from 'jotai';
import { v4 as uuidv4 } from 'uuid';
import { messagesAtom, loadingAtom } from '../states/atoms';
import type { BubbleProps } from '@ant-design/x';
import type { GetProp, GetRef, UploadFile } from 'antd';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Line, Bar, Pie, Doughnut, Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
} from 'chart.js';
import './chatStyles.css';
import { Message, ChartData, CustomFile } from '../types'; // 统一使用 types 中定义的类型

// 注册ChartJS组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  ChartTooltip,
  Legend,
);

// 定义消息内容结构
type MessageContent = {
  analysis?: string;
  charts?: ChartData[];
  strategy?: string;
  [key: string]: any;
};

// 定义气泡项类型
type BubbleItem = BubbleProps & {
  key: string | number;
  role: string;
  content: string | MessageContent;
};

// 动态图表组件 - 根据类型渲染不同图表
const DynamicChart: React.FC<{ chartData: ChartData }> = ({ chartData }) => {
  const { type, data, title } = chartData;

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: type === 'pie' || type === 'doughnut' ? ('right' as const) : ('top' as const),
      },
      title: {
        display: true,
        text: title,
      },
    },
    // 横向条形图特殊处理
    ...(type === 'bar' && data.labels && data.labels.length <= 5
      ? { indexAxis: 'y' as const }
      : {}),
  };

  switch (type) {
    case 'bar':
      return <Bar data={data} options={options} />;
    case 'line':
      return <Line data={data} options={options} />;
    case 'pie':
      return <Pie data={data} options={options} />;
    case 'doughnut':
      return <Doughnut data={data} options={options} />;
    case 'scatter':
      // 散点图特殊处理
      return <Scatter data={data} options={options} />;
    default:
      return <Bar data={data} options={options} />;
  }
};

// 渲染复杂内容（分析+图表+策略）
const renderComplexContent = (content: MessageContent) => {
  return (
    <div className="complex-content">
      {/* 渲染分析部分 */}
      {content.analysis && (
        <div className="analysis-section mb-4">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content.analysis}</ReactMarkdown>
        </div>
      )}

      {/* 渲染图表部分 */}
      {content.charts && content.charts.length > 0 && (
        <div className="charts-section mb-6">
          {content.charts.map(chart => (
            <div key={chart.id} className="chart-container my-6 p-4 bg-white rounded-lg shadow-sm">
              <h3 className="text-lg font-medium mb-2">{chart.title}</h3>
              {chart.description && <p className="text-gray-500 mb-3">{chart.description}</p>}
              <div style={{ height: '300px' }}>
                <DynamicChart chartData={chart} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 渲染策略部分 */}
      {content.strategy && (
        <div className="strategy-section">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content.strategy}</ReactMarkdown>
        </div>
      )}
    </div>
  );
};

// 内容渲染器 - 处理普通文本和复杂内容
const ContentRenderer: BubbleProps['messageRender'] = content => {
  // 如果内容不是字符串（可能是已解析的对象），尝试渲染复杂内容
  if (typeof content !== 'string') {
    try {
      // 尝试将content作为MessageContent对象处理
      const msgContent = content as unknown as MessageContent;
      if (msgContent.analysis || msgContent.charts || msgContent.strategy) {
        return renderComplexContent(msgContent);
      }
      // 如果不匹配MessageContent结构，转为字符串
      return <div>{JSON.stringify(content)}</div>;
    } catch (e) {
      console.error('Failed to render complex content:', e);
      return <div>无法显示内容</div>;
    }
  }

  // 尝试解析内容是否为JSON字符串
  try {
    const jsonContent = JSON.parse(content) as MessageContent;
    if (jsonContent.analysis || jsonContent.charts || jsonContent.strategy) {
      return renderComplexContent(jsonContent);
    }
  } catch (e) {
    // 不是JSON，作为普通Markdown处理
  }

  // 普通Markdown渲染
  return (
    <div className="markdown-content">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
};

// 气泡角色配置
const roles: GetProp<typeof Bubble.List, 'roles'> = {
  bot: {
    placement: 'start',
    avatar: {
      icon: <RobotOutlined />,
      style: { background: '#1677ff', color: 'white' },
    },
    typing: { step: 10, interval: 30 },
    style: {
      maxWidth: '100%',
    },
    variant: 'shadow',
    messageRender: ContentRenderer,
    loadingRender: () => (
      <Space>
        <Spin size="small" />
        正在思考...
      </Space>
    ),
  },
  analyst: {
    placement: 'start',
    avatar: {
      icon: <RobotOutlined />,
      style: { background: '#52c41a', color: 'white' },
    },
    style: { maxWidth: '100%' },
    variant: 'filled',
    messageRender: ContentRenderer,
  },
  strategist: {
    placement: 'start',
    avatar: {
      icon: <RobotOutlined />,
      style: { background: '#722ed1', color: 'white' },
    },
    style: { maxWidth: '100%' },
    variant: 'filled',
    messageRender: ContentRenderer,
  },
  error: {
    placement: 'start',
    avatar: {
      icon: <RobotOutlined />,
      style: { background: '#f5222d', color: 'white' },
    },
    style: { maxWidth: '100%' },
    variant: 'filled',
  },
  user: {
    placement: 'end',
    avatar: {
      icon: <UserOutlined />,
      style: { background: '#f0f2f5' },
    },
    style: { maxWidth: '100%' },
    variant: 'outlined',
  },
  file: {
    placement: 'end',
    avatar: { icon: <UserOutlined />, style: { visibility: 'hidden' } },
    variant: 'borderless',
    messageRender: (items: any) => (
      <Flex vertical gap="small">
        {(items as any[]).map(item => (
          <Attachments.FileCard key={item.uid} item={item} style={{ width: '100%' }} />
        ))}
      </Flex>
    ),
  },
};

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useAtom(messagesAtom);
  const [loading, setLoading] = useAtom(loadingAtom);
  const [query, setQuery] = useState<string>('');
  const [file, setFile] = useState<CustomFile | null>(null);
  const [uploadedFile, setUploadedFile] = useState<UploadFile | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const listRef = useRef<GetRef<typeof Bubble.List>>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [processingStage, setProcessingStage] = useState<string>('');

  // 转换消息格式以适配 Bubble.List
  const bubbleItems: BubbleItem[] = messages.map(msg => ({
    key: msg.id,
    role: msg.role || (msg.type === 'user' ? 'user' : 'bot'),
    content: msg.content,
  }));

  // 如果正在加载，添加加载中气泡
  if (loading) {
    bubbleItems.push({
      key: 'loading',
      role: 'bot',
      content: processingStage || '正在思考...',
      loading: true,
    } as BubbleItem);
  }

  // 监听消息变化，自动滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [bubbleItems.length]);

  // 使用ResizeObserver监听大小变化，保持滚动到底部
  useEffect(() => {
    if (!containerRef.current) return;

    const observer = new ResizeObserver(() => {
      scrollToBottom();
    });

    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
    };
  }, []);

  // 滚动到顶部函数
  const scrollToTop = () => {
    if (listRef.current && bubbleItems.length > 0) {
      const firstItemKey = bubbleItems[0].key;
      listRef.current.scrollTo({ key: firstItemKey, block: 'start', behavior: 'smooth' });
    }
  };

  // 滚动到底部函数
  const scrollToBottom = () => {
    setTimeout(() => {
      if (containerRef.current) {
        containerRef.current.scrollTop = containerRef.current.scrollHeight;
      }

      if (listRef.current && bubbleItems.length > 0) {
        const lastItemKey = bubbleItems[bubbleItems.length - 1].key;
        listRef.current.scrollTo({ key: lastItemKey, block: 'end', behavior: 'smooth' });
      }
    }, 100);
  };

  // 确保聊天窗口始终滚动到底部的函数
  const forceScrollToBottom = () => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  };

  // 修改uploadFile函数以返回正确格式的响应
  const uploadFile = async (file: CustomFile): Promise<CustomFile> => {
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      // 保存原始文件属性
      const originalSize = file.size;
      const originalName = file.name; // 显式保存名称

      console.log('上传文件到:', '/api/upload');

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('文件上传响应:', result);

      // 返回增强的文件对象，显式包含所有需要的属性
      return {
        ...file,
        name: originalName,
        size: originalSize,
        path: result.file_path || null,
        uploaded: true,
      };
    } catch (error) {
      console.error('Error uploading file:', error);
      message.error('文件上传失败');
      throw error;
    } finally {
      setUploading(false);
    }
  };

  // 发送分析请求
  const sendAnalysisRequest = async (filePath: string | null | undefined, userQuery: string) => {
    try {
      // 添加用户消息
      setMessages(prevMessages => [
        ...prevMessages,
        {
          id: uuidv4(),
          type: 'user',
          role: 'user',
          content: userQuery,
        },
      ]);

      // 初始化进度状态 - 不使用固定值
      setProgress(0);
      setProcessingStage('发送请求...');

      // 准备请求数据 - 包含消息历史以维持上下文
      const requestData = {
        file_path: filePath || '', // 提供默认值防止null/undefined
        query: userQuery,
        // 添加消息历史，仅包含最近5条
        message_history: messages
          .slice(-5)
          .filter(msg => typeof msg.content === 'string') // 只包含文本消息
          .map(msg => ({
            role: msg.role === 'user' ? 'user' : 'assistant',
            content: typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content),
          })),
        conversation_id: conversationId,
      };

      console.log('发送分析请求:', requestData);

      // 立即滚动到底部确保用户看到最新消息
      forceScrollToBottom();

      // 发送请求
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('分析响应:', result);

      // 从响应更新进度和状态 (如果后端提供)
      if (result.progress) {
        setProgress(result.progress);
      } else {
        setProgress(100); // 完成状态
      }

      if (result.stage) {
        setProcessingStage(result.stage);
      } else {
        setProcessingStage('处理完成');
      }

      // 保存服务器返回的 conversation_id
      if (result.conversation_id) {
        setConversationId(result.conversation_id);
        console.log('会话ID已保存:', result.conversation_id);
      }

      // 根据结果类型决定如何显示
      if (result.analysis || result.charts) {
        // 图表分析响应
        setMessages(prevMessages => [
          ...prevMessages,
          {
            id: uuidv4(),
            type: 'bot',
            role: 'analyst',
            content: {
              analysis: result.analysis,
              charts: result.charts || [],
            },
          },
        ]);

        // 如果有策略信息，也添加到消息列表
        if (result.strategy) {
          setMessages(prevMessages => [
            ...prevMessages,
            {
              id: uuidv4(),
              type: 'bot',
              role: 'strategist',
              content: {
                strategy: result.strategy,
              },
            },
          ]);
        }
      } else {
        // 普通文本响应
        setMessages(prevMessages => [
          ...prevMessages,
          {
            id: uuidv4(),
            type: 'bot',
            role: 'bot',
            content: result.answer || '无法获取有效回复',
          },
        ]);
      }

      // 再次强制滚动到底部，确保显示最新回复
      forceScrollToBottom();
      setTimeout(forceScrollToBottom, 300); // 额外延迟确保渲染完成后滚动
    } catch (error) {
      console.error('Analysis error:', error);
      message.error('处理请求时出错: ' + (error instanceof Error ? error.message : String(error)));

      // 添加错误消息
      setMessages(prevMessages => [
        ...prevMessages,
        {
          id: uuidv4(),
          type: 'bot',
          role: 'error',
          content: `处理请求时出错: ${error instanceof Error ? error.message : String(error)}`,
        },
      ]);

      // 滚动到底部显示错误消息
      forceScrollToBottom();
    } finally {
      setLoading(false);
      setProgress(0);
      setProcessingStage('');
    }
  };

  // 发送分析请求
  const handleSend = async () => {
    if (!query.trim() || loading) {
      return;
    }

    // 设置loading状态
    setLoading(true);

    try {
      // 确保文件已上传
      let filePath = null;
      if (file) {
        if (!file.path) {
          // 如果文件未上传，先上传
          const uploadedFile = await uploadFile(file);
          // 更新状态中的文件
          setFile(uploadedFile);
          filePath = uploadedFile.path;
        } else {
          filePath = file.path;
        }
      }

      // 检查文件是否有路径
      if (file && !filePath) {
        message.error('文件准备失败，无法获取文件路径');
        setLoading(false);
        return;
      }

      // 发送分析请求
      await sendAnalysisRequest(filePath, query);

      // 清空输入
      setQuery('');

      // 焦点回到输入框，方便用户继续提问
      if (inputRef.current) {
        inputRef.current.focus();
      }
    } catch (error) {
      console.error('Analysis error:', error);
      message.error('处理请求时出错，请重试');
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 文件上传前验证
  const beforeUpload = (file: File) => {
    const isCSV = file.type === 'text/csv';
    const isExcel =
      file.type === 'application/vnd.ms-excel' ||
      file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

    if (!isCSV && !isExcel) {
      message.error('只能上传CSV或Excel文件!');
      return Upload.LIST_IGNORE;
    }

    // 文件大小限制: 10MB
    const isLessThan10M = file.size / 1024 / 1024 < 10;
    if (!isLessThan10M) {
      message.error('文件必须小于10MB!');
      return Upload.LIST_IGNORE;
    }

    // 设置文件 - 转换为CustomFile类型
    const customFile = file as CustomFile;
    setFile(customFile);
    setUploadedFile({
      uid: '-1',
      name: file.name,
      status: 'done',
      size: file.size,
      type: file.type,
    });

    return false; // 阻止自动上传
  };

  return (
    <Flex vertical className="h-full">
      {/* 滚动控制 */}
      <Flex justify="flex-end" align="center" className="px-4 pt-2 pb-1">
        <Space>
          <Tooltip title="滚动到顶部">
            <Button
              type="text"
              icon={<VerticalAlignTopOutlined />}
              onClick={scrollToTop}
              size="small"
            />
          </Tooltip>
          <Tooltip title="滚动到底部">
            <Button
              type="text"
              icon={<VerticalAlignBottomOutlined />}
              onClick={scrollToBottom}
              size="small"
            />
          </Tooltip>
        </Space>
      </Flex>

      {/* 聊天消息区域 */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto bg-gray-50 rounded-lg px-4 py-4 mb-4 bubble-container"
      >
        <Bubble.List
          ref={listRef}
          roles={roles}
          items={bubbleItems}
          autoScroll={false} // 关闭自动滚动，我们手动控制
          className="full-width-bubbles"
        />
      </div>

      {/* 进度显示 */}
      {loading && processingStage && (
        <div className="px-4 mb-2">
          <Progress
            percent={progress}
            status="active"
            size="small"
            strokeColor={{
              '0%': '#108ee9',
              '100%': '#87d068',
            }}
          />
          <div className="text-xs text-gray-500 mt-1">{processingStage}</div>
        </div>
      )}

      {/* 文件上传显示区 */}
      {file && (
        <Card size="small" className="mx-4 mb-4 bg-blue-50">
          <Flex justify="space-between" align="center">
            <Flex align="center" gap="small">
              <UploadOutlined />
              <span className="text-sm text-gray-700 truncate" style={{ maxWidth: '200px' }}>
                {file.name}
              </span>
              {/* 添加安全检查 */}
              {file.size !== undefined ? (
                <span className="text-xs text-gray-500">({(file.size / 1024).toFixed(1)} KB)</span>
              ) : (
                <span className="text-xs text-gray-500">(大小未知)</span>
              )}
            </Flex>
            <Button
              type="text"
              icon={<DeleteOutlined />}
              size="small"
              onClick={() => {
                setFile(null);
                setUploadedFile(null);
              }}
              disabled={loading}
            />
          </Flex>
        </Card>
      )}

      {/* 输入区域 - 增加内边距，避免贴边 */}
      <div className="px-4 pb-4">
        <Flex gap="small">
          <Upload
            beforeUpload={beforeUpload}
            showUploadList={false}
            accept=".csv,.xlsx,.xls"
            disabled={loading || uploading}
          >
            <Button
              icon={<UploadOutlined />}
              disabled={loading || uploading}
              title="上传CSV或Excel文件"
              loading={uploading}
            />
          </Upload>

          <Input.TextArea
            ref={inputRef}
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入问题..."
            autoSize={{ minRows: 1, maxRows: 3 }}
            disabled={loading}
            className="flex-1"
          />

          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            disabled={loading || !query.trim()}
            title="发送分析请求"
            className={loading ? 'disabled-button' : 'enabled-button'}
          />
        </Flex>
      </div>
    </Flex>
  );
};

export default ChatInterface;
