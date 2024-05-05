import React, { useState } from 'react';
import { Modal, Input, InputNumber, Button, Form, message } from 'antd';
import FormItem from 'antd/es/form/FormItem';
import axios from 'axios';

const MyModal = ({ visible, handleCancel, onUpdate }) => {
  const [name, setName] = useState('');
  const [price, setPrice] = useState(0);
  const [loading, setLoading] = useState(false);
  const [messageApi, contextHolder] = message.useMessage();

  const handleSave = () => {
    // Включаем индикатор загрузки и делаем все элементы неактивными
    setLoading(true);

    // Отправляем данные на сервер
    axios.post('http://localhost:8000/ingredient/', { name, price })
      .then(response => {
        // Здесь можно обработать успешный ответ от сервера
        console.log('Data saved successfully:', response.data);
        onUpdate();
        setName('');
        setPrice(0);
        handleCancel();
      })
      .catch(error => {
        // Здесь можно обработать ошибку при отправке данных на сервер
        handleCancel();
        messageApi.error('Could not create an Ingredient');
        console.error('Error saving data:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <Modal
      title="Add Item"
      visible={visible}
      onCancel={handleCancel}
      footer={[
        // Кнопка "OK" с индикатором загрузки
        <Button key="ok" type="primary" onClick={handleSave} loading={loading}>
          OK
        </Button>,
      ]}
    >
      {/* Поле ввода имени */}
      <Form>
        <FormItem label='Name'>
        <Input
        title='Name'
        style={{width: 350}}
        placeholder="Name"
        value={name}
        disabled={loading}
        onChange={(e) => setName(e.target.value)}
      />
      </FormItem>
      <FormItem label='Price'>
      <InputNumber
        title='Price'
        placeholder="Price"
        value={price}
        disabled={loading}
        onChange={(value) => setPrice(value)}
        style={{ width: 70 }}
      />
      </FormItem>
      </Form>
    </Modal>
  );
};

export default MyModal;
