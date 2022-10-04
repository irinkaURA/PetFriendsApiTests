from api import PetFriends
from settings import valid_email, valid_password
import os
import pytest

pf = PetFriends()

class TestPetFriends:
    def setup(self):
        self.pet_id = None

    def test_get_api_key_for_valid_user(self, email=valid_email, password=valid_password):
        """ Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""

        # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
        status, result = pf.get_api_key(email, password)

        # Сверяем полученные данные с нашими ожиданиями
        assert status == 200
        assert 'key' in result


    def test_get_all_pets_with_valid_key(self, filter=''):
        """ Проверяем что запрос всех питомцев возвращает не пустой список.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
        запрашиваем список всех питомцев и проверяем что список не пустой.
        Доступное значение параметра filter - 'my_pets' либо '' """

        _, auth_key = pf.get_api_key(valid_email, valid_password)
        status, result = pf.get_list_of_pets(auth_key, filter)

        assert status == 200
        assert len(result['pets']) > 0

    def test_add_new_pet_with_valid_data(self, name='Барбоскин', animal_type='двортерьер',
                                         age='4', pet_photo='images/cat1.jpg'):
        """Проверяем что можно добавить питомца с корректными данными"""

        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name

    def test_add_new_pet_simple_with_valid_data(self, name='Барбоскин', animal_type='двортерьер',
                                         age='4'):
        """Проверяем что можно добавить питомца с корректными данными"""

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name

    def test_set_pet_photo_with_valid_data(self, name='Балбескин', animal_type='хрюнтерьер',
                                                age='4', pet_photo='images/cat1.jpg'):
        """Проверяем, что можно добавить картинку питомца в формате JPEG, как заявлено в документации"""

        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

        # Добавляем питомца
        status, result = pf.set_pet_photo(auth_key, result['id'], pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name

    def test_successful_delete_self_pet(self):
        """Проверяем возможность удаления питомца"""

        # Получаем ключ auth_key и запрашиваем список своих питомцев
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
        if len(my_pets['pets']) == 0:
            pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
            _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        # Берём id первого питомца из списка и отправляем запрос на удаление
        pet_id = my_pets['pets'][0]['id']
        status, _ = pf.delete_pet(auth_key, pet_id)

        # Ещё раз запрашиваем список своих питомцев
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
        assert status == 200
        assert pet_id not in my_pets.values()


    def test_successful_update_self_pet_info(self, name='Мурзик', animal_type='Котэ', age=5):
        """Проверяем возможность обновления информации о питомце"""

        # Получаем ключ auth_key и список своих питомцев
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
        if len(my_pets['pets']) > 0:
            status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

            # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
            assert status == 200
            assert result['name'] == name
        else:
            # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
            raise Exception("There is no my pets")

###############################################################################################
######################################## HOME WORK ############################################
###############################################################################################

    def test_get_api_key_for_invalid_user(self, email=valid_email, password=valid_password):
        """ Проверяем, что запрос api ключа неверного пользователя возвращает статус 403 и в результате содержится слово key"""

        # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
        status, result = pf.get_api_key('email', 'password')

        # Сверяем полученные данные с нашими ожиданиями
        assert status == 403
        assert 'key' in result

    def test_get_all_pets_with_invalid_key(self, filter=''):
        """ Проверяем, что запрос на список питомцев с неверным Api key возвращает статус отличный от 200 """

        auth_key = {'key': 'invalid_key'}
        status, result = pf.get_list_of_pets(auth_key, filter)

        assert status != 200
        assert len(result['pets']) > 0

    def test_get_all_pets_with_invalid_filter(self, filter='invalid_filter'):
        """ Проверяем, что запрос на получение питомцев с неверным фильтром возвращает статус отличный от 200"""

        _, auth_key = pf.get_api_key(valid_email, valid_password)
        status, result = pf.get_list_of_pets(auth_key, filter)

        assert status != 200

    def test_add_new_pet_with_invalid_data(self, name='', animal_type='',
                                         age='', pet_photo='images/cat1.jpg'):
        """Проверяем, что добавление питомца с пустым именем/возрастом/типом возвращает статус отличный от 200"""

        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status != 200
        assert result['name'] == name

    def test_add_new_pet_simple_with_invalid_data(self, name='', animal_type='',
                                                age=''):
        """Проверяем, что добавление питомца с пустым именем/возрастом/типом возвращает статус отличный от 200 через create_pet_simple"""

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status != 200
        assert result['name'] == name

    def test_add_new_pet_with_valid_png_photo(self, name='Тестовыйзверь5', animal_type='зверь',
                                         age='100', pet_photo='images/cat1.png'):
        """Проверяем, что можно добавить картинку питомца в формате PNG, как я заявлено в документации"""

        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo, 'image/png')

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name
        assert len(result['pet_photo']) > 0

    def test_set_pet_photo_with_invalid_png_photo(self, name='Балбескин', animal_type='хрюнтерьер',
                                           age='4', pet_photo='images/cat1.png'):
        """Проверяем, что при добавлении картинки питомца в формате PNG и Content-Type для картинки image/jpeg, серевер вернет статус 500"""

        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

        # Добавляем питомца
        status, result = pf.set_pet_photo(auth_key, result['id'], pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 500
        assert result['name'] == name
        assert len(result['pet_photo']) > 0

    def test_unsuccessful_delete_pet_with_invalid_id(self):
        """Проверяем возможность удаления питомца через неверный pet_id, сервер должен вернуть статус отличный от 200"""

        # Получаем ключ auth_key и запрашиваем список своих питомцев
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        status, result = pf.delete_pet(auth_key, 'invalid_pet_id')

        # Проверяем что статус ответа не равен 200
        assert status != 200

    def test_unsuccessful_delete_self_pet_with_invalid_id(self):
        """Проверяем возможность удаления чужого питомца, сервер должен вернуть статус 403"""

        # Получаем ключ auth_key и запрашиваем список своих питомцев
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, pets = pf.get_list_of_pets(auth_key, "")
        # Если список не пустой, то пробуем удалить последнего питомца
        if len(pets['pets']) > 0:
            status, result = pf.delete_pet(auth_key, pets['pets'][0]['id'])

        # Проверяем что статус ответа не равен 200
        assert status == 403

    def test_successful_update_self_pet_info(self, name='Мурзик', animal_type='Котэ', age=5):
        """Проверяем возможность обновления информации о чужом питомце, ответ сервера должен быть 403"""

        # Получаем ключ auth_key и список своих питомцев
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, pets = pf.get_list_of_pets(auth_key, "")

        # Если список не пустой, то пробуем обновить его имя, тип и возраст
        if len(pets['pets']) > 0:
            status, result = pf.update_pet_info(auth_key, pets['pets'][0]['id'], name, animal_type, age)

            # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
            assert status == 403
            assert result['name'] == name
        else:
            # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
            raise Exception("There is no my pets")
