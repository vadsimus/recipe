import { useEffect, useMemo, useState } from 'react';
import { Button, Form, Input, InputNumber, Modal, Popconfirm, Select, Table, Tag, Typography, message } from 'antd';
import { AppleOutlined, DeleteOutlined, EditOutlined, PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { deleteData, fetchData, postData, putData } from '@/services/ant-design-pro/api';

const { Title, Text } = Typography;

interface Ingredient {
  id: number;
  name: string;
  cost: string;
  unit: string;
  cost_unit: string;
  calories: string;
  calories_unit: string;
}

const unitLabels: Record<string, { label: string; color: string }> = {
  g: { label: 'граммы', color: 'gold' },
  l: { label: 'литры', color: 'blue' },
  pcs: { label: 'штуки', color: 'purple' },
};

const IngredientsPage = () => {
  const [form] = Form.useForm();
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [editingIngredient, setEditingIngredient] = useState<Ingredient | null>(null);

  const loadIngredients = async () => {
    setLoading(true);
    const res = await fetchData<Ingredient[]>({ endpoint: '/api/ingredients/' });
    setIngredients(res?.data || []);
    setLoading(false);
  };

  useEffect(() => {
    loadIngredients();
  }, []);

  const filteredIngredients = useMemo(
    () => ingredients.filter((i) => i.name.toLowerCase().includes(search.trim().toLowerCase())),
    [ingredients, search],
  );

  const openAddModal = () => {
    setEditingIngredient(null);
    form.resetFields();
    form.setFieldsValue({ unit: 'g', cost_unit: '1kg', calories_unit: '1kg' });
    setModalVisible(true);
  };

  const openEditModal = (ingredient: Ingredient) => {
    setEditingIngredient(ingredient);
    form.setFieldsValue({
      name: ingredient.name,
      cost: parseFloat(ingredient.cost),
      unit: ingredient.unit,
      cost_unit: ingredient.cost_unit || '1kg',
      calories: parseFloat(ingredient.calories),
      calories_unit: ingredient.calories_unit || '1kg',
    });
    setModalVisible(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingIngredient) {
        await putData({ endpoint: `/api/ingredients/${editingIngredient.id}/`, data: values });
        message.success('Ингредиент обновлён');
      } else {
        await postData({ endpoint: '/api/ingredients/', data: values });
        message.success('Ингредиент добавлен');
      }
      setModalVisible(false);
      form.resetFields();
      loadIngredients();
    } catch (error) {
      message.error('Ошибка при сохранении');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteData({ endpoint: `/api/ingredients/${id}/` });
      message.success('Удалено');
      loadIngredients();
    } catch (error) {
      message.error('Ошибка при удалении');
    }
  };

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
            Ингредиенты
          </Title>
          <Text type="secondary">{ingredients.length} ингредиент(ов)</Text>
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
          <Button type="primary" icon={<PlusOutlined />} onClick={openAddModal}>
            Добавить ингредиент
          </Button>
        </div>
      </div>

      <div style={{ background: '#fff', borderRadius: 16, overflow: 'hidden', boxShadow: '0 2px 10px -4px rgba(43, 33, 24, 0.12)' }}>
        <Table<Ingredient>
          rowKey="id"
          loading={loading}
          dataSource={filteredIngredients}
          pagination={{ pageSize: 10, hideOnSinglePage: true }}
          locale={{ emptyText: 'Ингредиенты не найдены' }}
          columns={[
            {
              title: 'Название',
              dataIndex: 'name',
              render: (name) => (
                <Text style={{ fontWeight: 500 }}>
                  <AppleOutlined style={{ color: '#2F9E44', marginRight: 8 }} />
                  {name}
                </Text>
              ),
            },
            {
              title: 'Тип',
              dataIndex: 'unit',
              width: 130,
              render: (unit) => <Tag color={unitLabels[unit]?.color || 'default'}>{unitLabels[unit]?.label || unit}</Tag>,
            },
            {
              title: 'Стоимость',
              dataIndex: 'cost',
              render: (cost, record) => `$${cost} за ${record.cost_unit || '1kg'}`,
            },
            {
              title: 'Калории',
              dataIndex: 'calories',
              render: (calories, record) => `${calories} ккал за ${record.calories_unit || '1kg'}`,
            },
            {
              title: '',
              width: 100,
              render: (_, record) => (
                <div style={{ display: 'flex', gap: 4, justifyContent: 'flex-end' }}>
                  <Button type="text" icon={<EditOutlined />} onClick={() => openEditModal(record)} />
                  <Popconfirm title="Удалить ингредиент?" onConfirm={() => handleDelete(record.id)}>
                    <Button type="text" danger icon={<DeleteOutlined />} />
                  </Popconfirm>
                </div>
              ),
            },
          ]}
        />
      </div>

      <Modal
        title={editingIngredient ? 'Редактировать ингредиент' : 'Добавить ингредиент'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={handleSubmit}
        okText="Сохранить"
        cancelText="Отмена"
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Название" rules={[{ required: true, message: 'Введите название' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="unit" label="Тип единицы измерения" rules={[{ required: true, message: 'Выберите тип единицы' }]}>
            <Select>
              <Select.Option value="g">Граммы (g)</Select.Option>
              <Select.Option value="l">Литры (l)</Select.Option>
              <Select.Option value="pcs">Штуки (pcs)</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="cost" label="Стоимость" rules={[{ required: true, message: 'Введите стоимость' }]}>
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="cost_unit" label="Стоимость за" rules={[{ required: true, message: 'Выберите единицу стоимости' }]}>
            <Select>
              <Select.Option value="1kg">1 кг</Select.Option>
              <Select.Option value="100g">100 г</Select.Option>
              <Select.Option value="500g">500 г</Select.Option>
              <Select.Option value="1l">1 л</Select.Option>
              <Select.Option value="100ml">100 мл</Select.Option>
              <Select.Option value="500ml">500 мл</Select.Option>
              <Select.Option value="1pcs">1 штука</Select.Option>
              <Select.Option value="10pcs">10 штук</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="calories" label="Калории" rules={[{ required: true, message: 'Введите калорийность' }]}>
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="calories_unit" label="Калории за" rules={[{ required: true, message: 'Выберите единицу калорийности' }]}>
            <Select>
              <Select.Option value="1kg">1 кг</Select.Option>
              <Select.Option value="100g">100 г</Select.Option>
              <Select.Option value="500g">500 г</Select.Option>
              <Select.Option value="1l">1 л</Select.Option>
              <Select.Option value="100ml">100 мл</Select.Option>
              <Select.Option value="500ml">500 мл</Select.Option>
              <Select.Option value="1pcs">1 штука</Select.Option>
              <Select.Option value="10pcs">10 штук</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default IngredientsPage;
