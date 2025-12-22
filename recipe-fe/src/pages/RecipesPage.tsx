import {useEffect, useState} from 'react';
import {
    Button,
    Card,
    Col,
    Form,
    Input,
    InputNumber,
    Modal,
    Row,
    Select,
    Space,
    Upload,
    message,
    Typography, Popconfirm,
} from 'antd';
import {PlusOutlined, UploadOutlined} from '@ant-design/icons';
import {deleteData, fetchData, postData, putData} from '@/services/ant-design-pro/api';

const {Text, Paragraph} = Typography;

interface IngredientOption {
    id: number;
    name: string;
    unit: string;
}

interface RecipeIngredient {
    id: number;
    name: string;
    cost: string;
    unit: string;
    ingredient_amount: number;
    ingredient_price: string;
}

interface Recipe {
    id: number;
    name: string;
    description: string;
    image?: string;
    ingredients: RecipeIngredient[];
    total_price: string;
}

const RecipesPage = () => {
    const [recipes, setRecipes] = useState<Recipe[]>([]);
    const [ingredientsOptions, setIngredientsOptions] = useState<IngredientOption[]>([]);
    const [modalVisible, setModalVisible] = useState(false);
    const [form] = Form.useForm();
    const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
    const [editMode, setEditMode] = useState(false);
    const [uploadingImage, setUploadingImage] = useState(false);
    const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null);
    const [uploadedImageFile, setUploadedImageFile] = useState<File | null>(null);

    useEffect(() => {
        loadRecipes();
        loadIngredients();
    }, []);

    const loadRecipes = async () => {
        const res = await fetchData({endpoint: '/api/recipes/'});
        if (res?.data) {
            setRecipes(res.data);
        }
    };

    const loadIngredients = async () => {
        const res = await fetchData({endpoint: '/api/ingredients/'});
        if (res?.data) {
            setIngredientsOptions(res.data);
        }
    };

    const openCreateModal = () => {
        setSelectedRecipe(null);
        setUploadedImageUrl(null);
        setUploadedImageFile(null);
        setEditMode(true);
        form.resetFields();
        setModalVisible(true);
    };

    const openViewModal = (recipe: Recipe) => {
        setSelectedRecipe(recipe);
        setUploadedImageUrl(`${window.location.origin}${recipe.image?.startsWith('/') ? '' : '/'}${recipe.image}` || null);
        setUploadedImageFile(null);
        setEditMode(false);

        // Format ingredient amounts to remove trailing zeros but preserve precision
        const formatAmount = (value: number): number => {
            // Convert to string with enough precision, then remove trailing zeros
            const str = value.toFixed(6);
            // Remove trailing zeros but keep at least one decimal place if needed
            const cleaned = str.replace(/\.?0+$/, '');
            return parseFloat(cleaned);
        };
        
        form.setFieldsValue({
            name: recipe.name,
            description: recipe.description,
            ingredients: recipe.ingredients.map((i) => ({
                ingredient_id: i.id,
                ingredient_amount: formatAmount(i.ingredient_amount),
                display_unit: i.unit,
            })),
        });

        setModalVisible(true);
    };

    const uploadImage = async (recipeId: number, file: File) => {
        try {
            setUploadingImage(true);
            const formData = new FormData();
            formData.append('image', file);

            const res = await postData({
                endpoint: `/api/recipes/${recipeId}/upload-image/`,
                data: formData,
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            if (res.result !== 'ok' || !res.data) {
                throw new Error(`Ошибка загрузки картинки: ${res.statusText}`);
            }

            message.success('Картинка загружена');
            // Обновить данные рецептов после успешной загрузки картинки
            await loadRecipes();
        } catch (error) {
            console.error(error);
            message.error('Ошибка загрузки картинки');
        } finally {
            setUploadingImage(false);
        }
    };

    const handleSave = async () => {
        try {
            const values = await form.validateFields();

            let recipeId: number | null = null;

            if (selectedRecipe) {
                await putData({
                    endpoint: `/api/recipes/${selectedRecipe.id}/`,
                    data: values,
                });
                message.success('Рецепт обновлён');
                recipeId = selectedRecipe.id;
            } else {
                const res = await postData({
                    endpoint: '/api/recipes/',
                    data: values,
                });
                message.success('Рецепт создан');
                recipeId = res?.data?.id;
            }

            if (uploadedImageFile && recipeId) {
                await uploadImage(recipeId, uploadedImageFile);
            }

            // Обновляем список рецептов
            const res = await fetchData({endpoint: '/api/recipes/'});
            if (res?.data) {
                setRecipes(res.data);

                // Найдем обновлённый рецепт в списке и поставим в selectedRecipe
                const updatedRecipe = res.data.find((r: Recipe) => r.id === recipeId) || null;
                setSelectedRecipe(updatedRecipe);
            }

            setEditMode(false);
        } catch (e) {
            console.error(e);
            message.error('Ошибка при сохранении рецепта');
        }
    };


    const uploadProps = {
        beforeUpload: (file: File) => {
            // Можно добавить валидацию типа и размера файла
            setUploadedImageFile(file);

            // Превью локально
            const previewUrl = URL.createObjectURL(file);
            setUploadedImageUrl(previewUrl);

            return false; // отменяем авто загрузку
        },
        onRemove: () => {
            setUploadedImageFile(null);
            setUploadedImageUrl(null);
        },
        multiple: false,
        accept: 'image/*',
        showUploadList: true,
    };

    const handleDeleteRecipe = async (id: number) => {
        try {
            await deleteData({
                endpoint: `/api/recipes/${id}/`,
            });
            message.success('Рецепт удалён');
            // После удаления обновляем список рецептов
            await loadRecipes(); // предполагается, что loadRecipes доступна в области видимости
            // Закрываем модал, если открыт
            setModalVisible(false);
            setSelectedRecipe(null);
            setEditMode(false);
        } catch (error) {
            console.error(error);
            message.error('Ошибка при удалении рецепта');
        }
    }
    const totalPrice = form.getFieldValue('total_price') || selectedRecipe?.total_price || '0';


    return (
        <>
            <Button type="primary" onClick={openCreateModal} style={{marginBottom: 16}}>
                Добавить рецепт
            </Button>

            <Row gutter={[16, 16]}>
                {recipes.map((recipe) => (
                    <Col key={recipe.id} span={6}>
                        <Card
                            hoverable
                            cover={
                                recipe.image ? (
                                    <img
                                        alt={recipe.name}
                                        src={`${window.location.origin}${recipe.image.startsWith('/') ? '' : '/'}${recipe.image}`}
                                        style={{height: 180, objectFit: 'cover'}}
                                    />
                                ) : (
                                    <div style={{height: 180, backgroundColor: '#f0f0f0'}}/>
                                )
                            }
                            onClick={() => openViewModal(recipe)}
                        >
                            <Card.Meta title={recipe.name} description={`Стоимость: ${recipe.total_price}`}/>
                        </Card>
                    </Col>
                ))}
            </Row>

            <Modal
                open={modalVisible}
                width={800}
                title={
                    <>
                        {uploadedImageUrl && (
                            <img
                                src={uploadedImageUrl}
                                alt="Картинка рецепта"
                                style={{width: '100%', objectFit: 'cover', marginBottom: 12, borderRadius: 4}}
                            />
                        )}
                    </>
                }
                onCancel={() => {
                    if (editMode) {
                        openViewModal(selectedRecipe!);
                        setEditMode(false);
                    } else {
                        setModalVisible(false);
                        setEditMode(false);
                        setUploadedImageFile(null);
                        setUploadedImageUrl(null);
                        form.resetFields();
                    }
                }}
                footer={
                    <Space style={{display: 'flex', justifyContent: 'flex-end'}}>
                        {selectedRecipe && editMode && (
                            <Popconfirm
                                title="Вы уверены, что хотите удалить рецепт?"
                                onConfirm={() => handleDeleteRecipe(selectedRecipe.id)}
                                okText="Да"
                                cancelText="Нет"
                            >
                                <Button danger>
                                    Удалить
                                </Button>
                            </Popconfirm>
                        )}
                        {editMode && (
                            <Button type="primary" loading={uploadingImage} onClick={handleSave}>
                                Сохранить
                            </Button>
                        )}
                        {!editMode && (
                            <Button type="primary" onClick={() => setEditMode(true)}>
                                Редактировать
                            </Button>
                        )}
                        <Button
                            onClick={() => {
                                if (editMode) {
                                    // Отмена редактирования — возвращаем в режим просмотра
                                    openViewModal(selectedRecipe!);
                                    setEditMode(false);
                                } else {
                                    setModalVisible(false);
                                    setEditMode(false);
                                    setUploadedImageFile(null);
                                    setUploadedImageUrl(null);
                                    form.resetFields();
                                }
                            }}
                        >
                            {editMode ? 'Отмена' : 'Закрыть'}
                        </Button>
                    </Space>
                }
                destroyOnClose
            >
                <Form form={form} layout="vertical" initialValues={{ingredients: []}}>
                    {/* Название */}
                    <Form.Item name="name" label={editMode ? "Название" : ""} rules={[{required: true}]}>
                        {editMode ? <Input/> :
                            <Text style={{textAlign: 'center', fontWeight: 'bold', display: 'block'}}>
                                {form.getFieldValue('name') || '-'}
                            </Text>}
                    </Form.Item>

                    {/* Описание */}
                    <Form.Item name="description" label={editMode ? "Описание" : ""} rules={[{required: true}]}>
                        {editMode ? <Input.TextArea rows={4}/> :
                            <Paragraph>{form.getFieldValue('description') || '-'}</Paragraph>}
                    </Form.Item>

                    {/* Ингредиенты */}
                    {!editMode && selectedRecipe && (
                        <div style={{marginBottom: 8, paddingBottom: 8, borderBottom: '1px solid #f0f0f0'}}>
                            <Space style={{display: 'flex', width: '100%'}}>
                                <Text style={{width: 180, fontWeight: 600}}>Ингредиент</Text>
                                <Text style={{width: 120, fontWeight: 600}}>Количество</Text>
                                <Text style={{width: 100, textAlign: 'right', fontWeight: 600}}>Цена</Text>
                            </Space>
                        </div>
                    )}
                    <Form.List name="ingredients">
                        {(fields, {add, remove}) => (
                            <>
                                {fields.map(({key, name, ...restField}) => {
                                    const ingredientId = form.getFieldValue(['ingredients', name, 'ingredient_id']);
                                    const ingredientAmountRaw = form.getFieldValue(['ingredients', name, 'ingredient_amount']);
                                    const displayUnit = form.getFieldValue(['ingredients', name, 'display_unit']);
                                    const ingredientName = ingredientsOptions.find((i) => i.id === ingredientId)?.name || '-';
                                    const selectedIngredient = ingredientsOptions.find((i) => i.id === ingredientId);
                                    const ingredientUnit = selectedIngredient?.unit || 'g';
                                    
                                    // Format amount to remove trailing zeros but preserve precision for small values
                                    const formatAmount = (value: number | undefined): number | undefined => {
                                        if (value === undefined || value === null) return undefined;
                                        // Convert to string, remove trailing zeros, but keep at least one decimal if needed
                                        const str = value.toString();
                                        // If it's a whole number, return as integer
                                        if (Number.isInteger(value)) return value;
                                        // Otherwise, parse and return (removes trailing zeros automatically)
                                        return parseFloat(value.toFixed(6).replace(/\.?0+$/, ''));
                                    };
                                    const ingredientAmount = formatAmount(ingredientAmountRaw);
                                    
                                    // Get ingredient_price from selectedRecipe if in view mode
                                    const recipeIngredient = !editMode && selectedRecipe?.ingredients?.find((ing: RecipeIngredient) => ing.id === ingredientId);
                                    const ingredientPrice = recipeIngredient && typeof recipeIngredient !== 'boolean' ? recipeIngredient.ingredient_price : undefined;

                                    // Get available display units based on ingredient unit type
                                    const getDisplayUnitOptions = () => {
                                        if (ingredientUnit === 'g') {
                                            return [
                                                { label: 'кг', value: 'kg' },
                                                { label: 'г', value: 'g' },
                                            ];
                                        } else if (ingredientUnit === 'l') {
                                            return [
                                                { label: 'л', value: 'l' },
                                                { label: 'мл', value: 'ml' },
                                            ];
                                        } else {
                                            return [
                                                { label: 'шт', value: 'pcs' },
                                            ];
                                        }
                                    };

                                    return (
                                        <Space key={key} style={{display: 'flex', marginBottom: 8}} align="baseline">
                                            {editMode ? (
                                                <>
                                                    <Form.Item {...restField} name={[name, 'ingredient_id']}
                                                               rules={[{required: true}]}>
                                                        <Select
                                                            showSearch
                                                            placeholder="Ингредиент"
                                                            style={{width: 180}}
                                                            options={ingredientsOptions.map((i) => ({
                                                                label: i.name,
                                                                value: i.id,
                                                            }))}
                                                            filterOption={(input, option) =>
                                                                option?.label?.toLowerCase().includes(input.toLowerCase())
                                                            }
                                                            onChange={() => {
                                                                // Reset display_unit when ingredient changes
                                                                form.setFieldValue(['ingredients', name, 'display_unit'], undefined);
                                                            }}
                                                        />
                                                    </Form.Item>
                                                    <Form.Item {...restField} name={[name, 'ingredient_amount']}
                                                               rules={[{required: true}]}>
                                                        <InputNumber 
                                                            min={0} 
                                                            step={0.001} 
                                                            precision={6}
                                                            placeholder="Количество" 
                                                            style={{width: 120}}
                                                        />
                                                    </Form.Item>
                                                    {selectedIngredient && (
                                                        <Form.Item {...restField} name={[name, 'display_unit']}>
                                                            <Select placeholder="Единица" style={{width: 100}}>
                                                                {getDisplayUnitOptions().map(opt => (
                                                                    <Select.Option key={opt.value} value={opt.value}>
                                                                        {opt.label}
                                                                    </Select.Option>
                                                                ))}
                                                            </Select>
                                                        </Form.Item>
                                                    )}
                                                    <Button type="link" danger onClick={() => remove(name)}>
                                                        Удалить
                                                    </Button>
                                                </>
                                            ) : (
                                                <>
                                                    <Text style={{
                                                        width: 180,
                                                        display: 'inline-block'
                                                    }}>{ingredientName}</Text>
                                                    <Text style={{width: 120}}>{ingredientAmount} {displayUnit || ingredientUnit}</Text>
                                                    {ingredientPrice && (
                                                        <Text style={{width: 100, textAlign: 'right', fontWeight: 500}}>
                                                            ${parseFloat(ingredientPrice).toFixed(2)}
                                                        </Text>
                                                    )}
                                                </>
                                            )}
                                        </Space>
                                    );
                                })}
                                {editMode && (
                                    <Form.Item>
                                        <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined/>}>
                                            Добавить ингредиент
                                        </Button>
                                    </Form.Item>
                                )}
                            </>
                        )}
                    </Form.List>

                    {(editMode || !selectedRecipe) && (
                        <Form.Item label="Картинка рецепта">
                            <Upload {...uploadProps} listType="picture">
                                <Button icon={<UploadOutlined/>}>Выбрать файл или перетащить</Button>
                            </Upload>
                        </Form.Item>
                    )}
                    <Text style={{fontWeight: 'bold'}}>Стоимость: ${totalPrice}</Text>
                </Form>
            </Modal>
        </>
    );
};

export default RecipesPage;
