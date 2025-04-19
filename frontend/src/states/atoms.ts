import { atom } from 'jotai';
import { atomWithImmer } from 'jotai-immer';
import { ChartData, AnalysisResult, Message } from '../types';
import type { ThoughtChainItem } from '@ant-design/x';

// 消息列表状态
export const messagesAtom = atomWithImmer<Message[]>([
  {
    id: '1',
    type: 'bot',
    content: '你好！请上传一个CSV文件，并告诉我你想了解什么。',
  },
]);

// 文件状态
export const fileAtom = atom<File | null>(null);

// 加载状态
export const loadingAtom = atom<boolean>(false);

// 分析结果状态
export const analysisResultAtom = atom<AnalysisResult | null>(null);

// 输入查询状态
export const queryAtom = atom<string>('');

// 思维链状态
export const thoughtChainItemsAtom = atom<ThoughtChainItem[]>([]);
