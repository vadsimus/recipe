
import React, { useState, useEffect } from 'react';
import { Select, Input, Button, Space, Divider, InputNumber } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import IngredientModal from './IngredientModal';
import axios from 'axios';

const { Option } = Select;

const IngredientsSelector = (props) => {
  const [options, setOptions] = useState([]); // Состояние для опций с сервера
  const [formData, setFormData] = useState([{ ingredient: '', quantity: ''}]); // Состояние для данных формы
  const [ingredientModalOpen, setIngredientModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);

    const get_ingredients = () => {
        axios.get('http://localhost:8000/get_ingredients/')
      .then(response => {
        setOptions(response.data.data);
      })
      .catch(error => {
        console.error('Error fetching options:', error);
      });
    }

  useEffect(() => {
    get_ingredients();
  }, []);



  // Функция для обновления состояния формы
  const handleInputChange = (index, key, value) => {
    const newFormData = [...formData];
    newFormData[index][key] = value;
    setFormData(newFormData);
    props.setFormData(newFormData);
  };

  // Функция для добавления новой пары элементов
  const handleAddField = () => {
    setFormData([...formData, { ingredient: '', quantity: '' }]);
    props.setFormData([...formData, { ingredient: '', quantity: ''}]);
  };

  const handleRemoveField = (index) => {
    const newFormData = [...formData];
    newFormData.splice(index, 1);
    setFormData(newFormData);
    props.setFormData(newFormData);
  };

  const onIngrediensUpdate = () => {
    get_ingredients()
  }


  return (
    <div>
      {/* Добавление полей формы */}
      {formData.map((field, index) => (
        <div key={index}>
          {/* Выбор ингредиента из списка */}
          <Space size="small" key={index} style={{marginTop:5}}>
          <Select
          loading={loading}
          disabled={loading}
            showSearch
            optionFilterProp="children"
            filterOption={(input, option) => {
                return (option?option.children.toLowerCase() : '').includes(input.toLowerCase())}
            }
            filterSort={(optionA, optionB) =>
            (optionA?.children ?? '').toLowerCase().localeCompare((optionB?.children ?? '').toLowerCase())
            }
            style={{ width: 300 }}
            placeholder="Select ingredient"
            onChange={(value) => handleInputChange(index, 'ingredient', value)}
            dropdownRender={(menu) => (
                <>
                  {menu}
                  <Divider style={{ margin: '8px 0' }} />
                  <Space style={{ padding: '0 8px 4px' }}>
                    <Button type="text" icon={<PlusOutlined />} style={{width:275}} onClick={()=>{setIngredientModalOpen(true)}}>
                      Add item
                    </Button>
                  </Space>
                </>
              )} 

          >
            {options.map(option => (
              <Option key={option.id} value={option.id}>{option.name}</Option>
            ))}
          </Select>

          {/* Ввод количества */}
          <InputNumber
            style={{ width: 70 }}
            // placeholder="Quantity"
            value={field.quantity}
            onChange={(e) => handleInputChange(index, 'quantity', e)}
          />

          {/* Кнопка для добавления новой пары элементов */}
          {index === formData.length - 1 && (
            <Button type="primary" onClick={handleAddField}><PlusOutlined /></Button>
          )}
            {index !== formData.length - 1 && (
            <Button danger type="text" onClick={() => handleRemoveField(index)} key={index}><DeleteOutlined /></Button>
          )}
            

          </Space>
          {/* <Button type="primary" onClick={handleSubmit} style={{ marginLeft: 10 }}>Submit</Button> */}
          <IngredientModal visible={ingredientModalOpen} handleCancel={()=>{setIngredientModalOpen(false)}} onUpdate={onIngrediensUpdate}/>
        </div>
      ))}
    </div>
  );
};

export default IngredientsSelector;
