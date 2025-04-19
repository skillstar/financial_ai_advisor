import React from 'react';
import { Layout, Flex, Typography } from 'antd';
import { BarChartOutlined } from '@ant-design/icons';

const { Header, Content } = Layout;
const { Title } = Typography;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <Layout className="h-screen overflow-hidden">
      <Header className="bg-[#1677ff] px-6 h-[64px] flex items-center shadow-md">
        <Flex align="center" gap="middle">
          <div className="flex items-center justify-center bg-white/20 rounded-full w-9 h-9">
            <BarChartOutlined className="text-lg text-white" />
          </div>
          <Title level={4} className="!text-white !m-0 select-none">
            CrewAI 数据分析平台
          </Title>
        </Flex>
      </Header>
      <Content className="flex-1 overflow-hidden">{children}</Content>
    </Layout>
  );
};

export default MainLayout;
