import React, { useState, useEffect } from 'react';
import { Drawer, Button } from 'antd';
import { Form, Input, Select } from 'antd';
import IngredientsSelector from './IngredientsSelector';
import axios from 'axios';


const { Option } = Select;

const Recipe = (props) => {

    // const [ingredientsData, setIngredientsData] = useState([]); // Состояние для данных ингредиентов
    // const [loading, setLoading] = useState(true)
    const [ingredients, setIngredients] = useState([{ ingredient: '', quantity: '' }])

    // useEffect(() => {
    //   // Здесь вы можете выполнить запрос к API для получения данных об ингредиентах
    //   // Здесь просто симулируем получение данных
    //   setTimeout(() => {
    //     const mockData = [
    //       { id: 1, name: 'Ingredient 1' },
    //       { id: 2, name: 'Ingredient 2' },
    //       { id: 3, name: 'Ingredient 3' }
    //     ];
    //     setIngredientsData(mockData);
    //     setLoading(false);
    //   }, 5000); // Имитация задержки в 1 секунду
    // }, []);

    const onFinish = (values) => {
        console.log('Received values:', values, ingredients);

        axios.post('http://localhost:8000/recipe/', { title: values.title, description: values.description, image_url: values.picture_url, ingredients: ingredients })
      .then(response => {
        // Здесь можно обработать успешный ответ от сервера
        console.log('Data saved successfully:', response.data);
      })
      .catch(error => {
        // Здесь можно обработать ошибку при отправке данных на сервер
        console.error('Error saving data:', error);
      })
      .finally(() => {
      });

      };

  return (
      <Drawer
    title="Recipe"
    placement="right"
    width={600}
    closable={true}
    onClose={props.handleCancel}
    open={props.visible}
  >

    <Form
      name="basic"
      initialValues={{ remember: true }}
      onFinish={onFinish}
      style={{ maxWidth: 400 }}
    >
      {/* Поле для ввода заголовка */}
      <Form.Item
        label="Title"
        name="title"
        rules={[{ required: true, message: 'Please input your title!' }]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        label="Picture"
        name="picture_url"
      >
        <Input />
      </Form.Item>

      {/* Поле для ввода описания */}
      <Form.Item
        label="Description"
        name="description"
        rules={[{ required: true, message: 'Please input your description!' }]}
      >
        <Input.TextArea />
      </Form.Item>

      {/* Поле для выбора ингредиентов */}
      <Form.Item
        label="Ingredients"
        name="ingredients"
      >
        <IngredientsSelector formData={ingredients} setFormData={setIngredients}/>



      </Form.Item>

      {/* Кнопка для отправки формы */}
      <Form.Item>
        <Button type="primary" htmlType="submit">
          Submit
        </Button>
      </Form.Item>
    </Form>




      </Drawer>
  );
};

export default Recipe;
