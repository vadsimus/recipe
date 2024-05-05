import React, { useState } from 'react';
import { Modal, Input, InputNumber, Button, Form, List } from 'antd';
import FormItem from 'antd/es/form/FormItem';

const RecipeModal = (props) => {
    const [name, setName] = useState('');
    const [price, setPrice] = useState(0);
    
    const image_url = props.currentItem ? props.currentItem.image_url : 'https://images.unsplash.com/photo-1606787366850-de6330128bfc?q=80&w=2970&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D';
    const ingredients = props.currentItem ? props.currentItem.ingredients : []
    console.log(ingredients)

  return (
    <div>
      <Modal
        title={props.currentItem && props.currentItem.name}
        open={props.openModal}
        onCancel={props.handleCancel}
        footer={[
          <Button key="submit" type="primary" onClick={props.handleCancel}>
            OK
          </Button>,
        ]}
      >
        <div style={{ marginBottom: 16 }}>
    {/* Изображение рецепта */}
    <img
        src={image_url}  // URL изображения рецепта
        alt={props.currentItem && props.currentItem.name}      // Текст для атрибута alt изображения
        style={{ maxWidth: '100%' }} // Стиль для максимальной ширины изображения (по ширине контейнера)
    />
</div>

{/* Название рецепта
<h3>{name}</h3> */}

{/* Описание рецепта */}
<p>{props.currentItem && props.currentItem.description}</p>

<List
        // pagination={{ position, align }}
        dataSource={ingredients}
        size="small"
        renderItem={(item, index) => (
          <List.Item>
            <List.Item.Meta
            //   avatar={<Avatar src={`https://api.dicebear.com/7.x/miniavs/svg?seed=${index}`} />}
              // title={item.name}
              description={<><span>{item.name}</span><span style={{marginLeft:30}}>{item.amount}</span><span style={{marginLeft: 50}}>{item.cost * item.amount}</span></>}
            />
          </List.Item>
        )}
      />
      <h2>Total price: {ingredients.length !== 0 ? ingredients.reduce((accumulator, currentValue) => accumulator + (parseFloat(currentValue.cost) * currentValue.amount), 0) : 0}</h2>

      </Modal>
      
    </div>
  );
};

export default RecipeModal;