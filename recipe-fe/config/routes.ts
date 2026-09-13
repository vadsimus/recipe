export default [
  {
    path: '/user',
    layout: false,
    routes: [
      {
        name: 'login',
        path: '/user/login',
        component: './User/Login',
      },
    ],
  },
  {
    path: '/recipes',
    name: 'Recipes',
    icon: 'book',
    component: './RecipesPage',
  },
  {
    path: '/recipes/:id',
    layout: false,
    component: './RecipeDetail',
  },
  {
    path: '/ingredients',
    name: 'Ingredients',
    icon: 'apple',
    component: './Ingredients',
  },
  {
    path: '/',
    redirect: '/recipes',
  },
  {
    path: '*',
    layout: false,
    component: './404',
  },
];
