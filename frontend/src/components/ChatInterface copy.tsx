import React, { useRef, useState, useEffect } from 'react';
import { Bubble, Attachments } from '@ant-design/x';
import { Button, Card, Flex, Input, Upload, Space, Spin, Tooltip } from 'antd';
import {
  SendOutlined,
  UploadOutlined,
  UserOutlined,
  RobotOutlined,
  DeleteOutlined,
  VerticalAlignTopOutlined,
  VerticalAlignBottomOutlined,
} from '@ant-design/icons';
import { useAtom, useAtomValue } from 'jotai';
import { v4 as uuidv4 } from 'uuid';
import { messagesAtom, loadingAtom } from '../states/atoms';
import { useAnalysisApi } from '../hooks/useAnalysisApi';
import type { BubbleProps } from '@ant-design/x';
import type { GetProp, GetRef } from 'antd';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
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

// 定义气泡项类型
type BubbleItem = BubbleProps & {
  key: string | number;
  role: string;
};

// 图表组件
const SalesChart = () => {
  const data = {
    labels: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
    datasets: [
      {
        label: '销售额(万元)',
        data: [25.3, 28.5, 24.3, 30.5, 33.2, 35.6, 37.5, 29.8, 36.4, 42.2, 49.2, 52.8],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        tension: 0.1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '月度销售趋势',
      },
    },
  };

  return <Line data={data} options={options} />;
};

const QuarterlyChart = () => {
  const data = {
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    datasets: [
      {
        label: '销售额(万元)',
        data: [78.1, 99.3, 103.7, 144.2],
        backgroundColor: [
          'rgba(54, 162, 235, 0.5)',
          'rgba(75, 192, 192, 0.5)',
          'rgba(255, 206, 86, 0.5)',
          'rgba(255, 99, 132, 0.5)',
        ],
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '季度销售对比',
      },
    },
  };

  return <Bar data={data} options={options} />;
};

const CategoryChart = () => {
  const data = {
    labels: ['电子产品', '服装', '食品', '家居用品', '运动器材'],
    datasets: [
      {
        label: '销售额(万元)',
        data: [158.0, 95.0, 85.0, 52.0, 35.3],
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right' as const,
      },
      title: {
        display: true,
        text: '产品类别销售分布',
      },
    },
  };

  return <Doughnut data={data} options={options} />;
};

const TopProductsChart = () => {
  const data = {
    labels: ['智能手机', '笔记本电脑', '运动鞋', '智能手表', '耳机'],
    datasets: [
      {
        label: '销售额(万元)',
        data: [64.5, 52.0, 32.0, 28.5, 23.0],
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
      },
    ],
  };

  const options = {
    indexAxis: 'y' as const,
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '销售额最高的产品',
      },
    },
  };

  return <Bar data={data} options={options} />;
};

// Markdown渲染器增强版 - 支持图表渲染
const MarkdownRenderer: BubbleProps['messageRender'] = content => {
  if (typeof content !== 'string') return content;

  // 检查特殊标记来插入图表
  if (content.includes('[SALES_CHART]')) {
    const parts = content.split('[SALES_CHART]');
    return (
      <div className="markdown-content">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{parts[0]}</ReactMarkdown>
        <div className="chart-container my-4">
          <SalesChart />
        </div>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{parts[1]}</ReactMarkdown>
      </div>
    );
  }

  if (content.includes('[QUARTERLY_CHART]')) {
    const parts = content.split('[QUARTERLY_CHART]');
    return (
      <div className="markdown-content">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{parts[0]}</ReactMarkdown>
        <div className="chart-container my-4">
          <QuarterlyChart />
        </div>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{parts[1]}</ReactMarkdown>
      </div>
    );
  }

  if (content.includes('[CATEGORY_CHART]')) {
    const parts = content.split('[CATEGORY_CHART]');
    return (
      <div className="markdown-content">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{parts[0]}</ReactMarkdown>
        <div className="chart-container my-4">
          <CategoryChart />
        </div>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{parts[1]}</ReactMarkdown>
      </div>
    );
  }

  if (content.includes('[TOP_PRODUCTS_CHART]')) {
    const parts = content.split('[TOP_PRODUCTS_CHART]');
    return (
      <div className="markdown-content">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{parts[0]}</ReactMarkdown>
        <div className="chart-container my-4">
          <TopProductsChart />
        </div>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{parts[1]}</ReactMarkdown>
      </div>
    );
  }

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
    style: { maxWidth: '100%' },
    variant: 'filled',
    messageRender: MarkdownRenderer,
    loadingRender: () => (
      <Space>
        <Spin size="small" />
        正在思考...
      </Space>
    ),
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

// 示例数据 - 带图表标记
const demoData = [
  {
    id: '1',
    type: 'user',
    content: '分析一下这个CSV文件中的销售数据，关注销售趋势和季节性波动。',
  },
  {
    id: '2',
    type: 'bot',
    content: `我已经分析了您提供的销售数据，以下是主要发现：  

### 销售趋势分析  

从数据可以看出，过去两年销售额整体呈上升趋势，年增长率约为12.5%。  

[SALES_CHART]  

### 季节性波动  

数据显示明显的季节性模式：  
- **第四季度**（10-12月）销售额最高，可能与年终促销和节假日消费有关  
- **第一季度**（1-3月）销售相对较低，呈现淡季特征  
- **夏季月份**销售有小幅上升，但波动较大  

[QUARTERLY_CHART]  

### 建议  

1. 在第四季度加大营销投入，充分利用旺季优势  
2. 为第一季度设计特殊促销活动，提升淡季销售  
3. 优化库存管理，根据季节性波动调整采购计划  

需要更深入的分析或有任何其他问题，请随时告诉我。`,
  },
  {
    id: '3',
    type: 'user',
    content: '各产品类别的销售情况如何？有哪些表现最好和最差的产品？',
  },
  {
    id: '4',
    type: 'bot',
    content: `我分析了各产品类别的销售情况，以下是详细分析：  

### 产品类别销售分布  

总体来看，电子产品占据最大份额，而家居用品的销售额最低。  

[CATEGORY_CHART]  

### 表现最佳的产品  

以下是销售额最高的五款产品：  

[TOP_PRODUCTS_CHART]  

### 表现最差的产品  

销售额最低的五款产品：  
1. 厨房小工具 - 58,000元  
2. 书籍 - 65,000元  
3. 办公用品 - 72,000元  
4. 装饰品 - 78,000元  
5. 床上用品 - 85,000元  

### 增长最快的产品类别  

过去一年增长最快的是电子产品类别，同比增长24.5%，主要得益于智能设备的普及。  

### 建议  

1. 扩大电子产品的库存和产品线，特别是智能手机和笔记本电脑  
2. 考虑减少或调整家居用品类别的投入  
3. 对床上用品和装饰品进行促销活动提升销量  
4. 优化产品组合，将资源集中在高利润和高销量的产品上  

需要更具体的产品销售数据分析，请随时告诉我。`,
  },
  {
    id: '5',
    type: 'user',
    content: '可以分析下各地区的销售情况和客户购买习惯吗？',
  },
  {
    id: '6',
    type: 'bot',
    content: `我分析了各地区销售数据和客户购买习惯，发现了一些有趣的模式：  

### 地区销售分布  

华东地区和华南地区是我们的主要市场，而西北地区的销售相对较弱。  

| 地区 | 销售额(万元) | 占比 | 同比增长 |  
|------|------------|------|---------|  
| 华东 | 152.6 | 35.8% | +18.2% |  
| 华南 | 124.3 | 29.2% | +15.5% |  
| 华北 | 86.7 | 20.3% | +8.3% |  
| 西南 | 42.1 | 9.9% | +12.6% |  
| 西北 | 20.5 | 4.8% | +5.2% |  

### 客户购买习惯  

分析表明客户购买行为存在明显的时间和渠道偏好：  

1. **购买时间**  
   - 工作日的晚间（18:00-22:00）订单量最高  
   - 周末中午（11:00-14:00）是第二个高峰期  
   - 节假日期间购买频率提高25%  

2. **购买渠道**  
   - 移动端占总订单的68%，且比例持续增长  
   - 电脑端占27%，主要用于较大金额的购买  
   - 实体店占5%，但客单价比线上高32%  

3. **复购率**  
   - 电子产品类别的客户90天复购率为35%  
   - 服装类别90天复购率最高，达到48%  
   - 家居用品复购周期最长，平均180天  

### 建议行动计划  

1. 针对华东和华南地区推出VIP客户计划，提高忠诚度  
2. 在西北地区增加营销投入，挖掘市场潜力  
3. 优化移动端购物体验，重点关注高峰时段的系统稳定性  
4. 针对不同品类设计差异化的复购激励策略  

需要更详细的客户行为分析或有其他问题，请随时告知。`,
  },
];

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useAtom(messagesAtom);
  const loading = useAtomValue(loadingAtom);
  const { runAnalysis } = useAnalysisApi();
  const [query, setQuery] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const listRef = useRef<GetRef<typeof Bubble.List>>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 使用示例数据 - 实际项目中移除这行
  const displayMessages = demoData; // 替换为 messages

  // 转换消息格式以适配 Bubble.List
  const bubbleItems: BubbleItem[] = displayMessages.map(msg => ({
    key: msg.id,
    role: msg.type === 'user' ? 'user' : 'bot',
    content: msg.content,
  }));

  // 如果正在加载，添加加载中气泡
  if (loading) {
    bubbleItems.push({
      key: 'loading',
      role: 'bot',
      content: '',
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

  const handleSend = () => {
    if (!query.trim() || !file) return;

    // 执行分析
    runAnalysis(file, query);

    // 清空输入
    setQuery('');

    // 滚动到底部
    scrollToBottom();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Flex vertical className="h-full">
      {/* 滚动控制按钮 */}
      <Flex justify="flex-end" className="px-4 pt-2 pb-1">
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
        className="flex-1 overflow-auto bg-gray-50 rounded-lg px-4 py-4 mb-4 bubble-container" // 添加 bubble-container 类
      >
        <Bubble.List
          ref={listRef}
          roles={roles}
          items={bubbleItems}
          autoScroll={true}
          className="full-width-bubbles" // 添加自定义类
        />
      </div>

      {/* 文件上传显示区 */}
      {file && (
        <Card size="small" className="mx-4 mb-4 bg-blue-50">
          <Flex justify="space-between" align="center">
            <Flex align="center" gap="small">
              <UploadOutlined />
              <span className="text-sm text-gray-700 truncate" style={{ maxWidth: '200px' }}>
                {file.name}
              </span>
            </Flex>
            <Button
              type="text"
              icon={<DeleteOutlined />}
              size="small"
              onClick={() => setFile(null)}
            />
          </Flex>
        </Card>
      )}

      {/* 输入区域 - 增加内边距，避免贴边 */}
      <div className="px-4 pb-4">
        <Flex gap="small">
          <Upload
            beforeUpload={file => {
              setFile(file);
              return false;
            }}
            showUploadList={false}
            accept=".csv,.xlsx,.xls"
          >
            <Button icon={<UploadOutlined />} />
          </Upload>

          <Input.TextArea
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入问题分析数据..."
            autoSize={{ minRows: 1, maxRows: 3 }}
            disabled={loading || !file}
            className="flex-1"
          />

          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            disabled={loading || !query.trim() || !file}
          />
        </Flex>
      </div>
    </Flex>
  );
};

export default ChatInterface;
