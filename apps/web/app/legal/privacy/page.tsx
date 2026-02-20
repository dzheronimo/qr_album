import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Политика конфиденциальности | QR Album',
  description: 'Политика конфиденциальности сервиса QR Album',
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-lg rounded-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            Политика конфиденциальности
          </h1>
          
          <div className="prose prose-lg max-w-none">
            <p className="text-gray-600 mb-6">
              Последнее обновление: {new Date().toLocaleDateString('ru-RU')}
            </p>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                1. Введение
              </h2>
              <p className="text-gray-700 mb-4">
                QR Album серьезно относится к защите вашей конфиденциальности. 
                Данная политика объясняет, как мы собираем, используем и защищаем вашу информацию.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                2. Информация, которую мы собираем
              </h2>
              <h3 className="text-xl font-medium text-gray-900 mb-3">
                2.1 Информация, предоставляемая вами
              </h3>
              <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
                <li>Имя и адрес электронной почты при регистрации</li>
                <li>Контент альбомов, который вы создаете</li>
                <li>Сообщения и отзывы, которые вы отправляете</li>
              </ul>
              
              <h3 className="text-xl font-medium text-gray-900 mb-3">
                2.2 Информация, собираемая автоматически
              </h3>
              <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
                <li>IP-адрес и информация о браузере</li>
                <li>Данные об использовании сервиса</li>
                <li>Файлы cookie и аналогичные технологии</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                3. Как мы используем вашу информацию
              </h2>
              <p className="text-gray-700 mb-4">
                Мы используем собранную информацию для:
              </p>
              <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
                <li>Предоставления и улучшения наших сервисов</li>
                <li>Обработки ваших запросов и транзакций</li>
                <li>Связи с вами по вопросам сервиса</li>
                <li>Обеспечения безопасности и предотвращения мошенничества</li>
                <li>Соблюдения правовых обязательств</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                4. Обмен информацией
              </h2>
              <p className="text-gray-700 mb-4">
                Мы не продаем, не сдаем в аренду и не передаем вашу личную информацию третьим лицам, 
                за исключением случаев:
              </p>
              <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
                <li>С вашего явного согласия</li>
                <li>Для выполнения правовых обязательств</li>
                <li>Для защиты наших прав и безопасности</li>
                <li>С поставщиками услуг, которые помогают нам работать</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                5. Защита данных
              </h2>
              <p className="text-gray-700 mb-4">
                Мы принимаем разумные меры для защиты вашей информации от несанкционированного доступа, 
                изменения, раскрытия или уничтожения. Это включает:
              </p>
              <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
                <li>Шифрование данных при передаче и хранении</li>
                <li>Регулярные проверки безопасности</li>
                <li>Ограничение доступа к персональным данным</li>
                <li>Обучение сотрудников вопросам конфиденциальности</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                6. Ваши права
              </h2>
              <p className="text-gray-700 mb-4">
                В зависимости от вашего местоположения, вы можете иметь следующие права:
              </p>
              <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
                <li>Доступ к вашей персональной информации</li>
                <li>Исправление неточной информации</li>
                <li>Удаление вашей информации</li>
                <li>Ограничение обработки ваших данных</li>
                <li>Переносимость данных</li>
                <li>Возражение против обработки</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                7. Файлы cookie
              </h2>
              <p className="text-gray-700 mb-4">
                Мы используем файлы cookie и аналогичные технологии для улучшения вашего опыта использования сервиса. 
                Вы можете управлять настройками cookie в своем браузере.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                8. Хранение данных
              </h2>
              <p className="text-gray-700 mb-4">
                Мы храним вашу информацию только в течение времени, необходимого для достижения целей, 
                описанных в данной политике, или в соответствии с требованиями закона.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                9. Изменения в политике
              </h2>
              <p className="text-gray-700 mb-4">
                Мы можем обновлять данную политику конфиденциальности время от времени. 
                Мы уведомим вас о любых существенных изменениях, разместив новую политику на нашем сайте.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                10. Контактная информация
              </h2>
              <p className="text-gray-700 mb-4">
                Если у вас есть вопросы по данной политике конфиденциальности или вы хотите 
                воспользоваться своими правами, пишите: privacy@storyqr.ru, legal@storyqr.ru
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

