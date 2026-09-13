import { useEffect, useMemo, useState } from 'react';
import { Button, Col, Empty, Input, Row, Skeleton, Tag, Typography } from 'antd';
import { DollarOutlined, FireOutlined, PictureOutlined, PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { history } from '@umijs/max';
import { fetchData } from '@/services/ant-design-pro/api';

const { Title, Text } = Typography;

interface Recipe {
  id: number;
  name: string;
  description: string;
  image?: string;
  total_price: string;
  total_calories: string;
}

const resolveImageUrl = (image?: string) => {
  if (!image) return undefined;
  return `${window.location.origin}${image.startsWith('/') ? '' : '/'}${image}`;
};

const RecipeCard = ({ recipe }: { recipe: Recipe }) => (
  <Col xs={24} sm={12} md={8} lg={6} key={recipe.id}>
    <div
      className="hover-lift"
      onClick={() => history.push(`/recipes/${recipe.id}`)}
      style={{
        background: '#fff',
        borderRadius: 16,
        overflow: 'hidden',
        boxShadow: '0 2px 10px -4px rgba(43, 33, 24, 0.12)',
        height: '100%',
      }}
    >
      <div style={{ position: 'relative', height: 160, background: '#F3E9DE' }}>
        {recipe.image ? (
          <img
            alt={recipe.name}
            src={resolveImageUrl(recipe.image)}
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        ) : (
          <div
            style={{
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#D8C9B8',
              fontSize: 36,
            }}
          >
            <PictureOutlined />
          </div>
        )}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(180deg, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)',
          }}
        />
        <Text
          style={{
            position: 'absolute',
            left: 14,
            bottom: 10,
            right: 14,
            color: '#fff',
            fontWeight: 600,
            fontSize: 16,
            textShadow: '0 1px 4px rgba(0,0,0,0.35)',
          }}
          ellipsis
        >
          {recipe.name}
        </Text>
      </div>
      <div style={{ padding: '10px 14px', display: 'flex', gap: 8 }}>
        <Tag color="orange" style={{ margin: 0, borderRadius: 999, display: 'flex', alignItems: 'center', gap: 4 }}>
          <DollarOutlined /> {recipe.total_price}
        </Tag>
        <Tag color="green" style={{ margin: 0, borderRadius: 999, display: 'flex', alignItems: 'center', gap: 4 }}>
          <FireOutlined /> {recipe.total_calories} ккал
        </Tag>
      </div>
    </div>
  </Col>
);

const RecipesPage = () => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    (async () => {
      setLoading(true);
      const res = await fetchData<Recipe[]>({ endpoint: '/api/recipes/' });
      if (res?.data) {
        setRecipes(res.data);
      }
      setLoading(false);
    })();
  }, []);

  const filteredRecipes = useMemo(
    () => recipes.filter((r) => r.name.toLowerCase().includes(search.trim().toLowerCase())),
    [recipes, search],
  );

  return (
    <>
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 16,
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 24,
        }}
      >
        <div>
          <Title level={3} style={{ margin: 0 }}>
            Рецепты
          </Title>
          <Text type="secondary">{recipes.length} рецепт(ов)</Text>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <Input
            allowClear
            placeholder="Поиск по названию"
            prefix={<SearchOutlined style={{ color: '#B8ADA0' }} />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 240 }}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => history.push('/recipes/new')}>
            Добавить рецепт
          </Button>
        </div>
      </div>

      {loading ? (
        <Row gutter={[16, 16]}>
          {Array.from({ length: 8 }).map((_, i) => (
            <Col xs={24} sm={12} md={8} lg={6} key={i}>
              <Skeleton.Image style={{ width: '100%', height: 160, borderRadius: 16 }} active />
            </Col>
          ))}
        </Row>
      ) : filteredRecipes.length === 0 ? (
        <Empty
          description={recipes.length === 0 ? 'Пока нет рецептов' : 'Ничего не найдено'}
          style={{ marginTop: 80 }}
        >
          {recipes.length === 0 && (
            <Button type="primary" icon={<PlusOutlined />} onClick={() => history.push('/recipes/new')}>
              Добавить первый рецепт
            </Button>
          )}
        </Empty>
      ) : (
        <Row gutter={[16, 16]}>
          {filteredRecipes.map((recipe) => (
            <RecipeCard recipe={recipe} key={recipe.id} />
          ))}
        </Row>
      )}
    </>
  );
};

export default RecipesPage;
