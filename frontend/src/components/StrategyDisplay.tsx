import React from 'react';
import { Card, Typography, Tag, Steps } from 'antd';
import { BulbOutlined, StarOutlined, WarningOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { Step } = Steps;

interface StrategyDisplayProps {
  strategy: string;
}

const StrategyDisplay: React.FC<StrategyDisplayProps> = ({ strategy }) => {
  if (!strategy) {
    return null;
  }

  // 尝试解析策略中的关键点
  const extractKeyPoints = (text: string): string[] => {
    const points: string[] = [];
    const lines = text.split('\n');

    lines.forEach(line => {
      if (line.match(/^\d+\.\s/) || line.match(/^•\s/) || line.includes('建议')) {
        points.push(line.trim());
      }
    });

    return points.filter(p => p.length > 10).slice(0, 5);
  };

  const keyPoints = extractKeyPoints(strategy);

  return (
    <Card>
      <Title level={4} className="flex items-center">
        <BulbOutlined className="mr-2 text-[#faad14]" />
        策略建议
      </Title>

      <Paragraph className="whitespace-pre-line">{strategy}</Paragraph>

      {keyPoints.length > 0 && (
        <div className="mt-6">
          <Title level={5} className="flex items-center">
            <StarOutlined className="mr-2 text-[#52c41a]" />
            关键行动点
          </Title>

          <Steps direction="vertical" size="small" className="mt-4">
            {keyPoints.map((point, index) => (
              <Step key={index} title={`行动 ${index + 1}`} description={point} status="process" />
            ))}
          </Steps>
        </div>
      )}

      <div className="mt-6">
        <Title level={5} className="flex items-center">
          <WarningOutlined className="mr-2 text-[#ff4d4f]" />
          注意事项
        </Title>

        <Paragraph>
          以上策略建议基于提供的数据分析。实施前请结合具体业务环境和其他因素进行综合评估。
        </Paragraph>

        <div className="flex gap-2 flex-wrap">
          <Tag color="blue">数据驱动</Tag>
          <Tag color="green">实用建议</Tag>
          <Tag color="orange">需进一步分析</Tag>
        </div>
      </div>
    </Card>
  );
};

export default StrategyDisplay;
