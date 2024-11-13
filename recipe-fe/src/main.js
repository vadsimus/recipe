import React, { useState, useEffect } from 'react';
import { Select, Input, Button, List, Card, Avatar, Space, FloatButton } from 'antd';
import { SettingOutlined, EditOutlined, EllipsisOutlined, PlusOutlined } from '@ant-design/icons';
import axios from 'axios';
import Recipe from './components/Recipe';
import RecipeModal from './components/RecipeModal'


const { Option } = Select;
const { Meta } = Card;
const { Search } = Input;

const MyComponent = () => {
  // const [selectedOption, setSelectedOption] = useState('');
  // const [inputValue, setInputValue] = useState('');
  // const data = [
  //   {title: 'Title1', url: 'https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png', price: '10$', description: 'First description'},
  //   {title: 'Title2', url: 'https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png', price: '20$', description: 'Second descr 2'},
  //   {title: 'Title3', url: 'https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png', price: '30$', description: 'Third description3'},
  //   {title: 'Title4', url: 'https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png', price: '20$', description: 'Fourth description4'},
  //   {title: 'Title5', url: 'https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png', price: '50$', description: 'Fifth description5'},
  //   {title: 'Title6', url: 'https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png', price: '60$', description: 'sixth description6'},
  // ]
  const [listData, setListData] = useState([]);
  const [filteredData, setFilteredData] = useState([])
  const [search, setSearch] = useState('')
  const [recipeModalOpen, setRecipeModalOpen] = useState(false);
  const [currentItem, setCurrentItem] = useState(null);
  const [openModal, setOpenModal]=useState(false);

  useEffect(() => {
    axios.get('http://localhost:8000/recipes/')
      .then(response => {
        console.log(response.data)
        setListData(response.data);
        setFilteredData(response.data);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }, []);

  // const handleSelectChange = (value) => {
  //   setSelectedOption(value);
  // };

  // const handleInputChange = (e) => {
  //   setInputValue(e.target.value);
  // };

  // const handleButtonClick = () => {
  //   console.log('Selected option:', selectedOption);
  //   console.log('Input value:', inputValue);
  // };

  // const data = [
  //   {title: 'Title1', url: 'https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png', price: '10$', description: 'Short description'},
  //   {title: 'Title2', url: 'https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png', price: '20$', description: 'Short description2'},
  //   {title: 'Title3', url: 'https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png', price: '30$', description: 'Short description3'},
  //   {title: 'Title4', url: 'https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png', price: '40$', description: 'Short description4'},
  //   {title: 'Title5', url: 'https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png', price: '50$', description: 'Short description5'},
  //   {title: 'Title6', url: 'https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png', price: '60$', description: 'Short description6'},
  // ]

  const onSearch = () => {
    // console.log(search)
    const filtered_data = listData.filter(item => 
      item.name.toLowerCase().includes(search.toLowerCase()) ||
      item.description.toLowerCase().includes(search.toLowerCase())
  );
    setFilteredData(filtered_data)
  }

  return (
    <div>
      
      <Space size="middle" direction='vertical' style={{ display: 'flex', margin: 25 }}>
      <Search placeholder="input search" onChange={(e) => {setSearch(e.target.value)}} onSearch={onSearch} enterButton style={{width: 300}} />
  <List
    grid={{ gutter: 50}}
    dataSource={filteredData}
    renderItem={(item) => (
      <List.Item>
        <Card
    style={{ width: 300 }}
    cover={
      <div style={{width: '100%', height: 200, overflow: 'hidden'}}>
        <img
          style={{width:'100%', height: '100%', objectFit: 'cover'}}
          alt="example"
          src={item.image_url?item.image_url:'https://images.unsplash.com/photo-1606787366850-de6330128bfc?q=80&w=2970&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'}
        />
      </div>
    }
    actions={[
      <SettingOutlined key="setting" />,
      <EditOutlined key="edit" />,
      <EllipsisOutlined key="ellipsis" onClick={() => {
        console.log(item)
        setCurrentItem(item);
        setOpenModal(true)
      }}/>,
    ]}
  >
    <Meta
      // avatar={<Avatar src="https://api.dicebear.com/7.x/miniavs/svg?seed=8" />}
      title={item.name}
      description={<div>
        {/* <span>{item.description}</span> */}
        <div>{item.price}</div>
      </div>}
    />
  </Card>
      </List.Item>
    )}
  />
  </Space>
  <FloatButton type='primary' icon={<PlusOutlined />} onClick={() => setRecipeModalOpen(true)} />
  <Recipe visible={recipeModalOpen} handleCancel={() => {setRecipeModalOpen(false)}}/>
  <RecipeModal openModal={openModal} handleCancel={()=>{setOpenModal(false)}} currentItem={currentItem}/>
    </div>
  );
};

export default MyComponent;
