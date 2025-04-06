import { useEffect, useState } from "react";
import { Card, Spin, Alert } from "antd";
import {fetchData} from "@/services/ant-design-pro/api";

// const fetchData = async () => {
//   try {
//       const options = {"endpoint": "/api/get_ingredients"}
//     const response = await fetchData(options);
//     const result = await response.json();
//     return result;
//   } catch (error) {
//     throw new Error("Ошибка загрузки данных");
//   }
// };

const DataCard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData({"endpoint": "/api/get_ingredients/"})
      .then((result) => {
        if (result.result === "ok") {
          setData(result.data);
        } else {
          setError("Некорректный ответ API");
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" />;
  if (error) return <Alert message={error} type="error" showIcon />;

  return (
    <>
      {data?.map((item) => (
        <Card key={item.id} title={item.name} style={{ width: 300, marginBottom: 16 }}>
          <p>Стоимость: {item.cost}</p>
        </Card>
      ))}
    </>
  );
};

export default DataCard;
