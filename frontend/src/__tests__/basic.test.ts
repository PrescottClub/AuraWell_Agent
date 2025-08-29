import { describe, it, expect } from 'vitest';

describe('Frontend CI Test', () => {
  it('should pass basic test', () => {
    expect(1 + 1).toBe(2);
  });

  it('should test string operations', () => {
    const str = 'Hello World';
    expect(str).toContain('World');
    expect(str.toLowerCase()).toBe('hello world');
  });
});

describe('环境兼容性测试', () => {
  it('Node.js 环境正常', () => {
    expect(typeof process).toBe('object');
    expect(process.env).toBeDefined();
  });

  it('Vitest 测试框架正常', () => {
    expect(typeof describe).toBe('function');
    expect(typeof it).toBe('function');
    expect(typeof expect).toBe('function');
  });

  it('数组操作正常', () => {
    const arr = [1, 2, 3];
    expect(arr.length).toBe(3);
    expect(arr.includes(2)).toBe(true);
    expect(arr.map(x => x * 2)).toEqual([2, 4, 6]);
  });
});
