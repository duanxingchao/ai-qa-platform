-- 数据库迁移脚本：为scores表添加维度名称字段
-- 执行时间：2024-01-XX
-- 目的：支持动态评分维度名称存储

-- 检查scores表是否存在
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'scores') THEN
        RAISE EXCEPTION 'scores表不存在，请先创建基础表结构';
    END IF;
END $$;

-- 添加维度名称字段
ALTER TABLE scores 
ADD COLUMN IF NOT EXISTS dimension_1_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS dimension_2_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS dimension_3_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS dimension_4_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS dimension_5_name VARCHAR(50);

-- 为新字段添加注释
COMMENT ON COLUMN scores.dimension_1_name IS '第一个评分维度名称（如：信息准确性）';
COMMENT ON COLUMN scores.dimension_2_name IS '第二个评分维度名称（如：逻辑性）';
COMMENT ON COLUMN scores.dimension_3_name IS '第三个评分维度名称（如：流畅性）';
COMMENT ON COLUMN scores.dimension_4_name IS '第四个评分维度名称（如：创新性）';
COMMENT ON COLUMN scores.dimension_5_name IS '第五个评分维度名称（如：完整性）';

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_scores_answer_id ON scores(answer_id);
CREATE INDEX IF NOT EXISTS idx_scores_rated_at ON scores(rated_at DESC);

-- 验证字段是否添加成功
DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns 
    WHERE table_name = 'scores' 
    AND column_name LIKE 'dimension_%_name';
    
    IF col_count = 5 THEN
        RAISE NOTICE '✅ 成功添加5个维度名称字段到scores表';
    ELSE
        RAISE EXCEPTION '❌ 维度名称字段添加失败，当前数量: %', col_count;
    END IF;
END $$; 