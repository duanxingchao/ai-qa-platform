-- 清理非标准分类数据的SQL脚本
-- 将非标准分类映射到标准的16种分类

-- 更新 "账户管理类" 为 "账户管理"
UPDATE questions 
SET classification = '账户管理' 
WHERE classification = '账户管理类';

-- 更新 "技术问题类" 为 "技术问题"
UPDATE questions 
SET classification = '技术问题' 
WHERE classification = '技术问题类';

-- 更新 "功能使用类" 为 "产品使用"
UPDATE questions 
SET classification = '产品使用' 
WHERE classification = '功能使用类';

-- 更新 "系统配置类" 为 "系统优化"
UPDATE questions 
SET classification = '系统优化' 
WHERE classification = '系统配置类';

-- 更新 "数据处理类" 为 "数据分析"
UPDATE questions 
SET classification = '数据分析' 
WHERE classification = '数据处理类';

-- 查询更新结果
SELECT 
    classification,
    COUNT(*) as count
FROM questions 
WHERE classification IS NOT NULL AND classification != ''
GROUP BY classification 
ORDER BY count DESC;
