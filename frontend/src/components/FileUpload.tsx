import React from 'react';
import { Typography } from 'antd';
import { Attachments } from '@ant-design/x';
import { CloudUploadOutlined } from '@ant-design/icons';
import { useAtom } from 'jotai';
import { fileAtom } from '../states/atoms';

const { Text } = Typography;

interface FileUploadProps {
  disabled?: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ disabled = false }) => {
  const [file, setFile] = useAtom(fileAtom);

  const handleFileChange = (info: any) => {
    if (info.fileList && info.fileList.length > 0) {
      const latestFile = info.fileList[info.fileList.length - 1];
      setFile(latestFile.originFileObj);
    } else {
      setFile(null);
    }
  };

  return (
    <div className="mb-4">
      <Attachments
        beforeUpload={() => false}
        onChange={handleFileChange}
        items={file ? [{ uid: '1', name: file.name, status: 'done' }] : []}
        maxCount={1}
        disabled={disabled}
        accept=".csv"
        placeholder={{
          icon: <CloudUploadOutlined />,
          title: '上传CSV文件',
          description: '点击或拖拽CSV文件到此处',
        }}
      />
      {file && (
        <Text className="text-sm text-gray-500 mt-1 block">
          已上传: {file.name} ({(file.size / 1024).toFixed(2)} KB)
        </Text>
      )}
    </div>
  );
};

export default FileUpload;
