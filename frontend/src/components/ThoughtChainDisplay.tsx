import React from 'react';
import { ThoughtChain } from '@ant-design/x';
import { Card, Typography } from 'antd';
import { CheckCircleOutlined, InfoCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import { useAtomValue } from 'jotai';
import { thoughtChainItemsAtom } from '../states/atoms';
import type { ThoughtChainItem } from '@ant-design/x';

const { Title } = Typography;

// 获取图标
const getStatusIcon = (status: ThoughtChainItem['status']) => {
  switch (status) {
    case 'success':
      return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
    case 'error':
      return <InfoCircleOutlined style={{ color: '#ff4d4f' }} />;
    case 'pending':
      return <LoadingOutlined style={{ color: '#1677ff' }} />;
    default:
      return undefined;
  }
};

// 内容渲染
const renderContent = (content: string) => {
  if (!content) return null;

  // 将换行符分割的内容转为段落
  return (
    <div>
      {content.split('\n').map((line, index) => (
        <p key={index}>{line}</p>
      ))}
    </div>
  );
};

const ThoughtChainDisplay: React.FC = () => {
  const items = useAtomValue(thoughtChainItemsAtom);

  // 添加图标和转换内容
  const formattedItems = items.map(item => ({
    ...item,
    icon: getStatusIcon(item.status),
    content: typeof item.content === 'string' ? renderContent(item.content) : item.content,
  }));

  if (items.length === 0) {
    return null;
  }

  return (
    <Card>
      <Title level={5} className="mb-4">
        分析思考过程
      </Title>
      <ThoughtChain items={formattedItems} collapsible size="middle" />
    </Card>
  );
};

export default ThoughtChainDisplay;
