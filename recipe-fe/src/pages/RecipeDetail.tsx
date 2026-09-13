import { useEffect, useState, type ReactNode } from 'react';
import {
  Button,
  Col,
  Form,
  Input,
  InputNumber,
  Popconfirm,
  Row,
  Select,
  Skeleton,
  Space,
  Typography,
  Upload,
  message,
} from 'antd';
import {
  ArrowLeftOutlined,
  CameraOutlined,
  DeleteOutlined,
  DollarOutlined,
  EditOutlined,
  FireOutlined,
  PictureOutlined,
  PlusOutlined,
  SaveOutlined,
} from '@ant-design/icons';
import { history, useParams } from '@umijs/max';
import { deleteData, fetchData, postData, putData } from '@/services/ant-design-pro/api';

const { Title, Text, Paragraph } = Typography;

interface IngredientOption {
  id: number;
  name: string;
  unit: string;
}

interface RecipeIngredient {
  id: number;
  name: string;
  unit: string;
  ingredient_amount: number;
  ingredient_price: string;
  ingredient_calories: string;
}

interface Recipe {
  id: number;
  name: string;
  description: string;
  image?: string;
  ingredients: RecipeIngredient[];
  total_price: string;
  total_calories: string;
}

const resolveImageUrl = (image?: string | null) => {
  if (!image) return undefined;
  return `${window.location.origin}${image.startsWith('/') ? '' : '/'}${image}`;
};

const formatAmount = (value: number | undefined | null): number | undefined => {
  if (value === undefined || value === null) return undefined;
  if (Number.isInteger(value)) return value;
  return parseFloat(value.toFixed(6).replace(/\.?0+$/, ''));
};

const getDisplayUnitOptions = (ingredientUnit?: string) => {
  if (ingredientUnit === 'g') {
    return [
      { label: 'кг', value: 'kg' },
      { label: 'г', value: 'g' },
    ];
  }
  if (ingredientUnit === 'l') {
    return [
      { label: 'л', value: 'l' },
      { label: 'мл', value: 'ml' },
    ];
  }
  return [{ label: 'шт', value: 'pcs' }];
};

const StatCard = ({ icon, label, value, color }: { icon: ReactNode; label: string; value: string; color: string }) => (
  <div
    style={{
      flex: 1,
      background: '#fff',
      borderRadius: 14,
      padding: '16px 18px',
      boxShadow: '0 2px 10px -4px rgba(43, 33, 24, 0.12)',
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, color, fontSize: 13, fontWeight: 600 }}>
      {icon} {label}
    </div>
    <div style={{ fontSize: 24, fontWeight: 700, color: '#2B2118', marginTop: 4 }}>{value}</div>
  </div>
);

const RecipeDetail = () => {
  const { id } = useParams<{ id: string }>();
  const isNew = id === 'new';

  const [form] = Form.useForm();
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [ingredientsOptions, setIngredientsOptions] = useState<IngredientOption[]>([]);
  const [loading, setLoading] = useState(!isNew);
  const [editMode, setEditMode] = useState(isNew);
  const [saving, setSaving] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);

  // Subscribing here (rather than reading via form.getFieldValue inside Form.List's
  // render prop) makes this component re-render whenever an ingredient row's selection
  // changes, so the unit picker for a newly-selected row shows up immediately.
  const watchedIngredients: { ingredient_id?: number }[] = Form.useWatch('ingredients', form) || [];

  const loadIngredientOptions = async () => {
    const res = await fetchData<IngredientOption[]>({ endpoint: '/api/ingredients/' });
    if (res?.data) setIngredientsOptions(res.data);
  };

  const applyRecipeToForm = (r: Recipe) => {
    form.setFieldsValue({
      name: r.name,
      description: r.description,
      ingredients: r.ingredients.map((i) => ({
        ingredient_id: i.id,
        ingredient_amount: formatAmount(i.ingredient_amount),
        display_unit: i.unit,
      })),
    });
    setImageUrl(resolveImageUrl(r.image) || null);
  };

  const loadRecipe = async () => {
    setLoading(true);
    const res = await fetchData<Recipe>({ endpoint: `/api/recipes/${id}/` });
    if (res?.data) {
      setRecipe(res.data);
      applyRecipeToForm(res.data);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadIngredientOptions();
    if (!isNew) {
      loadRecipe();
    } else {
      form.setFieldsValue({ ingredients: [] });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const uploadImage = async (recipeId: number, file: File) => {
    const formData = new FormData();
    formData.append('image', file);
    await postData({
      endpoint: `/api/recipes/${recipeId}/upload-image/`,
      data: formData,
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);

      let recipeId = recipe?.id;
      if (isNew) {
        const res = await postData({ endpoint: '/api/recipes/', data: values });
        recipeId = res?.data?.id;
        message.success('Рецепт создан');
      } else {
        await putData({ endpoint: `/api/recipes/${recipeId}/`, data: values });
        message.success('Рецепт обновлён');
      }

      if (imageFile && recipeId) {
        await uploadImage(recipeId, imageFile);
      }

      setImageFile(null);
      setEditMode(false);

      if (isNew) {
        // Changing the id triggers the load effect below, which fetches the new recipe.
        history.replace(`/recipes/${recipeId}`);
      } else {
        const res = await fetchData<Recipe>({ endpoint: `/api/recipes/${recipeId}/` });
        if (res?.data) {
          setRecipe(res.data);
          applyRecipeToForm(res.data);
        }
      }
    } catch (e) {
      console.error(e);
      message.error('Ошибка при сохранении рецепта');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!recipe) return;
    try {
      await deleteData({ endpoint: `/api/recipes/${recipe.id}/` });
      message.success('Рецепт удалён');
      history.push('/recipes');
    } catch (e) {
      message.error('Ошибка при удалении рецепта');
    }
  };

  const uploadProps = {
    beforeUpload: (file: File) => {
      setImageFile(file);
      setImageUrl(URL.createObjectURL(file));
      return false;
    },
    onRemove: () => {
      setImageFile(null);
      setImageUrl(recipe ? resolveImageUrl(recipe.image) || null : null);
    },
    multiple: false,
    accept: 'image/*',
    showUploadList: false,
  };

  const cancelEdit = () => {
    if (isNew) {
      history.push('/recipes');
      return;
    }
    if (recipe) applyRecipeToForm(recipe);
    setImageFile(null);
    setEditMode(false);
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: '#FBF7F2', padding: 24 }}>
        <Skeleton active paragraph={{ rows: 8 }} />
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#FBF7F2' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '14px 24px',
          background: '#fff',
          borderBottom: '1px solid #F0E9DF',
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}
      >
        <Button icon={<ArrowLeftOutlined />} type="text" onClick={() => history.push('/recipes')} />
        <Title level={4} style={{ margin: 0, flex: 1 }}>
          {isNew ? 'Новый рецепт' : recipe?.name}
        </Title>
        <Space>
          {!isNew && !editMode && (
            <Popconfirm title="Удалить рецепт?" onConfirm={handleDelete} okText="Да" cancelText="Нет">
              <Button icon={<DeleteOutlined />} danger>
                Удалить
              </Button>
            </Popconfirm>
          )}
          {editMode ? (
            <>
              <Button onClick={cancelEdit}>Отмена</Button>
              <Button type="primary" icon={<SaveOutlined />} loading={saving} onClick={handleSave}>
                Сохранить
              </Button>
            </>
          ) : (
            <Button type="primary" icon={<EditOutlined />} onClick={() => setEditMode(true)}>
              Редактировать
            </Button>
          )}
        </Space>
      </div>

      <div style={{ maxWidth: 1040, margin: '0 auto', padding: 24 }}>
        <Form form={form} layout="vertical">
          <Row gutter={24}>
            <Col xs={24} md={15}>
              <div
                style={{
                  position: 'relative',
                  height: 260,
                  borderRadius: 16,
                  overflow: 'hidden',
                  background: '#F3E9DE',
                  marginBottom: 20,
                }}
              >
                {imageUrl ? (
                  <img src={imageUrl} alt={recipe?.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                ) : (
                  <div
                    style={{
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#D8C9B8',
                      fontSize: 48,
                    }}
                  >
                    <PictureOutlined />
                  </div>
                )}
                {editMode && (
                  <Upload {...uploadProps}>
                    <Button
                      icon={<CameraOutlined />}
                      style={{ position: 'absolute', right: 12, bottom: 12 }}
                    >
                      Изменить фото
                    </Button>
                  </Upload>
                )}
              </div>

              {editMode ? (
                <>
                  <Form.Item name="name" label="Название" rules={[{ required: true }]}>
                    <Input size="large" placeholder="Название рецепта" />
                  </Form.Item>
                  <Form.Item name="description" label="Описание" rules={[{ required: true }]}>
                    <Input.TextArea rows={4} placeholder="Описание рецепта" />
                  </Form.Item>
                </>
              ) : (
                <Paragraph style={{ color: '#5B5044' }}>{recipe?.description}</Paragraph>
              )}

              <Title level={5} style={{ marginBottom: 12 }}>
                Ингредиенты
              </Title>

              {!editMode && (
                <div style={{ background: '#fff', borderRadius: 14, overflow: 'hidden' }}>
                  {recipe?.ingredients.map((ing, idx) => (
                    <div
                      key={ing.id + '-' + idx}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        padding: '12px 16px',
                        borderBottom: idx < recipe.ingredients.length - 1 ? '1px solid #F5EEE4' : 'none',
                      }}
                    >
                      <Text style={{ flex: 1 }}>{ing.name}</Text>
                      <Text type="secondary" style={{ width: 110, textAlign: 'right' }}>
                        {formatAmount(ing.ingredient_amount)} {ing.unit}
                      </Text>
                      <Text style={{ width: 90, textAlign: 'right', fontWeight: 500 }}>
                        ${parseFloat(ing.ingredient_price).toFixed(2)}
                      </Text>
                      <Text style={{ width: 100, textAlign: 'right', fontWeight: 500, color: '#2F9E44' }}>
                        {parseFloat(ing.ingredient_calories).toFixed(0)} ккал
                      </Text>
                    </div>
                  ))}
                  {recipe?.ingredients.length === 0 && (
                    <Text type="secondary" style={{ padding: 16, display: 'block' }}>
                      Ингредиенты не добавлены
                    </Text>
                  )}
                </div>
              )}

              {editMode && (
                <Form.List name="ingredients">
                  {(fields, { add, remove }) => (
                    <div style={{ background: '#fff', borderRadius: 14, padding: 16 }}>
                      {fields.map(({ key, name, ...restField }) => {
                        const ingredientId = watchedIngredients[name]?.ingredient_id;
                        const selectedIngredient = ingredientsOptions.find((i) => i.id === ingredientId);

                        return (
                          <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline" wrap>
                            <Form.Item {...restField} name={[name, 'ingredient_id']} rules={[{ required: true }]} noStyle>
                              <Select
                                showSearch
                                placeholder="Ингредиент"
                                style={{ width: 200 }}
                                options={ingredientsOptions.map((i) => ({ label: i.name, value: i.id }))}
                                filterOption={(input, option) =>
                                  (option?.label as string)?.toLowerCase().includes(input.toLowerCase())
                                }
                                onChange={() => form.setFieldValue(['ingredients', name, 'display_unit'], undefined)}
                              />
                            </Form.Item>
                            <Form.Item {...restField} name={[name, 'ingredient_amount']} rules={[{ required: true }]} noStyle>
                              <InputNumber min={0} step={0.001} precision={6} placeholder="Кол-во" style={{ width: 110 }} />
                            </Form.Item>
                            {selectedIngredient && (
                              <Form.Item {...restField} name={[name, 'display_unit']} noStyle>
                                <Select placeholder="Ед." style={{ width: 90 }}>
                                  {getDisplayUnitOptions(selectedIngredient.unit).map((opt) => (
                                    <Select.Option key={opt.value} value={opt.value}>
                                      {opt.label}
                                    </Select.Option>
                                  ))}
                                </Select>
                              </Form.Item>
                            )}
                            <Button type="text" danger icon={<DeleteOutlined />} onClick={() => remove(name)} />
                          </Space>
                        );
                      })}
                      <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                        Добавить ингредиент
                      </Button>
                    </div>
                  )}
                </Form.List>
              )}
            </Col>

            <Col xs={24} md={9}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, position: 'sticky', top: 90 }}>
                <StatCard
                  icon={<DollarOutlined />}
                  label="Стоимость"
                  value={`$${recipe?.total_price ?? '0'}`}
                  color="#E8590C"
                />
                <StatCard
                  icon={<FireOutlined />}
                  label="Калории"
                  value={`${recipe?.total_calories ?? '0'} ккал`}
                  color="#2F9E44"
                />
              </div>
            </Col>
          </Row>
        </Form>
      </div>
    </div>
  );
};

export default RecipeDetail;
