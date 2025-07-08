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
    icon: 'smile',
    component: './RecipesPage',
  },
  {
    path: '/ingredients',
    name: 'Ingredients',
    icon: 'table',
    component: './Welcome',
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
