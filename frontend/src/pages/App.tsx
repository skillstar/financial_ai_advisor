import React from 'react';
import { Row, Col, Flex, Typography, Space, Drawer, Button, FloatButton } from 'antd';
import { useAtomValue, useAtom } from 'jotai';
import { CommentOutlined, CloseOutlined } from '@ant-design/icons';
import MainLayout from '../layouts/MainLayout';
import ChatInterface from '../components/ChatInterface';
import DataVisualization from '../components/DataVisualization';
import StrategyDisplay from '../components/StrategyDisplay';
import ThoughtChainDisplay from '../components/ThoughtChainDisplay';
import { loadingAtom, analysisResultAtom, thoughtChainItemsAtom } from '../states/atoms';

const App: React.FC = () => {
  const loading = useAtomValue(loadingAtom);
  const result = useAtomValue(analysisResultAtom);
  const thoughtChainItems = useAtomValue(thoughtChainItemsAtom);

  // 侧边抽屉控制
  const [drawerOpen, setDrawerOpen] = React.useState(false);

  return (
    <MainLayout>
      {/* 主要内容区 - 居中占据90%空间 */}
      <Flex vertical align="center" justify="center" className="min-h-[calc(100vh-64px)]">
        <div className="w-[90%] max-w-[1400px]">
          {result && (
            <Space direction="vertical" size="large" className="w-full">
              <DataVisualization
                charts={result.charts}
                analysis={result.analysis}
                loading={loading}
              />
              <StrategyDisplay strategy={result.strategy} />
            </Space>
          )}

          {!result && !loading && (
            <Flex
              vertical
              align="center"
              justify="center"
              className="h-[70vh] bg-gray-50 rounded-lg border border-gray-200"
            >
              <Typography.Title level={3}>CrewAI 数据分析平台</Typography.Title>
              <Typography.Paragraph className="text-center text-gray-500 mt-4 max-w-md">
                点击右下角的对话按钮，上传CSV文件并提出分析问题。
                <br />
                <br />
                我们的AI将为您生成数据可视化和策略建议。
              </Typography.Paragraph>
            </Flex>
          )}
        </div>
      </Flex>

      {/* 右下角悬浮对话按钮 */}
      <FloatButton
        icon={<CommentOutlined />}
        type="primary"
        onClick={() => setDrawerOpen(true)}
        tooltip="打开对话"
      />

      {/* 抽屉式对话界面 */}
      <Drawer
        title="数据分析对话"
        placement="right"
        onClose={() => setDrawerOpen(false)}
        open={drawerOpen}
        width="50%" // 改为占屏幕的一半
        styles={{
          body: {
            padding: '0 16px', // 添加水平内边距
            display: 'flex',
            flexDirection: 'column',
            height: 'calc(100% - 55px)',
          },
          header: {
            paddingTop: 16,
            paddingBottom: 16,
            borderBottom: '1px solid #f0f0f0',
          },
        }}
        closeIcon={<CloseOutlined />}
      >
        <div className="flex-1 overflow-hidden">
          <ChatInterface />
        </div>
      </Drawer>
    </MainLayout>
  );
};

export default App;
