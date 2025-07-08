import { useRef, useState } from 'react';
import { ProTable, ActionType } from '@ant-design/pro-components';
import { Button, Form, Input, InputNumber, Modal, Popconfirm, message } from 'antd';
import {deleteData, fetchData, postData, putData} from '@/services/ant-design-pro/api';

interface Ingredient {
  id: number;
  name: string;
  cost: string;
}

const IngredientsPage = () => {
  const actionRef = useRef<ActionType>();
  const [form] = Form.useForm();
  const [modalVisible, setModalVisible] = useState(false);
  const [editingIngredient, setEditingIngredient] = useState<Ingredient | null>(null);

  const openAddModal = () => {
    setEditingIngredient(null);
    form.resetFields();
    setModalVisible(true);
  };

  const openEditModal = (ingredient: Ingredient) => {
    setEditingIngredient(ingredient);
    form.setFieldsValue({
      name: ingredient.name,
      cost: parseFloat(ingredient.cost),
    });
    setModalVisible(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();

      if (editingIngredient) {
        await putData({
          endpoint: `/api/ingredients/${editingIngredient.id}/`,
          data: values,
        });
        message.success('Ингредиент обновлён');
      } else {
        await postData({
          endpoint: '/api/ingredients/',
          data: values,
        });
        message.success('Ингредиент добавлен');
      }

      setModalVisible(false);
      form.resetFields();
      actionRef.current?.reload();
    } catch (error) {
      message.error('Ошибка при сохранении');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteData({
        endpoint: `/api/ingredients/${id}/`,
      });
      message.success('Удалено');
      actionRef.current?.reload();
    } catch (error) {
      message.error('Ошибка при удалении');
    }
  };

  return (
    <>
      <ProTable<Ingredient>
        headerTitle="Ингредиенты"
        rowKey="id"
        actionRef={actionRef}
        search={false}
        request={async () => {
          const res = await fetchData({ endpoint: '/api/ingredients/' });
          return {
            data: res?.data || [],
            success: res?.result === 'ok',
          };
        }}
        columns={[
          {
            title: 'Название',
            dataIndex: 'name',
          },
          {
            title: 'Стоимость за единицу',
            dataIndex: 'cost',
          },
          {
            title: 'Действия',
            valueType: 'option',
            render: (_, record) => [
              <a key="edit" onClick={() => openEditModal(record)}>Редактировать</a>,
              <Popconfirm
                key="delete"
                title="Удалить ингредиент?"
                onConfirm={() => handleDelete(record.id)}
              >
                <a style={{ color: 'red' }}>Удалить</a>
              </Popconfirm>,
            ],
          },
        ]}
        toolBarRender={() => [
          <Button type="primary" onClick={openAddModal} key="add">
            Добавить ингредиент
          </Button>,
        ]}
      />

      <Modal
        title={editingIngredient ? 'Редактировать ингредиент' : 'Добавить ингредиент'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={handleSubmit}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="Название"
            rules={[{ required: true, message: 'Введите название' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="cost"
            label="Стоимость за единицу"
            rules={[{ required: true, message: 'Введите стоимость' }]}
          >
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default IngredientsPage;
