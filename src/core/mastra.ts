import { z, ZodType } from 'zod';

/**
 * Mastra 风格的工作流框架实现
 * 提供 createStep 和 createWorkflow 功能
 */

export interface StepContext<T = any> {
  context: T;
}

export interface Step<TInput = any, TOutput = any> {
  id: string;
  description: string;
  inputSchema: ZodType<TInput>;
  outputSchema: ZodType<TOutput>;
  execute: (params: StepContext<TInput>) => Promise<TOutput>;
}

export interface Workflow<TInput = any, TOutput = any> {
  id: string;
  name: string;
  description: string;
  inputSchema: ZodType<TInput>;
  outputSchema: ZodType<TOutput>;
  steps: Step[];
  execute: (params: { input: TInput }) => Promise<TOutput>;
}

/**
 * 创建工作流步骤
 * @param config - 步骤配置
 * @returns Step 对象
 */
export function createStep<TInput = any, TOutput = any>(config: {
  id: string;
  description: string;
  inputSchema: ZodType<TInput>;
  outputSchema: ZodType<TOutput>;
  execute: (params: StepContext<TInput>) => Promise<TOutput>;
}): Step<TInput, TOutput> {
  return {
    id: config.id,
    description: config.description,
    inputSchema: config.inputSchema,
    outputSchema: config.outputSchema,
    execute: config.execute,
  };
}

/**
 * 创建工作流
 * @param config - 工作流配置
 * @returns Workflow 对象
 */
export function createWorkflow<TInput = any, TOutput = any>(config: {
  id: string;
  name: string;
  description: string;
  inputSchema: ZodType<TInput>;
  outputSchema: ZodType<TOutput>;
  steps: Step[];
  execute: (params: { input: TInput }) => Promise<TOutput>;
}): Workflow<TInput, TOutput> {
  return {
    id: config.id,
    name: config.name,
    description: config.description,
    inputSchema: config.inputSchema,
    outputSchema: config.outputSchema,
    steps: config.steps,
    execute: async (params: { input: TInput }) => {
      // 验证输入
      const validatedInput = config.inputSchema.parse(params.input);

      // 执行工作流
      const result = await config.execute({ input: validatedInput });

      // 验证输出
      const validatedOutput = config.outputSchema.parse(result);

      return validatedOutput;
    },
  };
}
