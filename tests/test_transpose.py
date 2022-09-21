from cmath import inf
import pytest

transpose_apis = ["/simple", "/explicit", "/raw"]


@pytest.mark.parametrize("api", transpose_apis)
def test_simple_vector(client, api):
    vector = [1, 2, 3, 4, 5]
    response = client.post(api, json=vector)
    assert response.status_code == 200
    assert response.json == [[1], [2], [3], [4], [5]]


@pytest.mark.parametrize("api", transpose_apis)
def test_simple_matrix(client, api):
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    response = client.post(api, json=matrix)
    assert response.status_code == 200
    assert response.json == [[1, 4, 7], [2, 5, 8], [3, 6, 9]]


@pytest.mark.parametrize("api", transpose_apis)
def test_row_matrix(client, api):
    matrix = [[1, 2, 3, 4, 5]]
    response = client.post(api, json=matrix)
    assert response.status_code == 200
    assert response.json == [[1], [2], [3], [4], [5]]


@pytest.mark.parametrize("api", transpose_apis)
def test_column_matrix(client, api):
    matrix = [[1], [2], [3], [4], [5]]
    response = client.post(api, json=matrix)
    assert response.status_code == 200
    assert response.json == [[1, 2, 3, 4, 5]]


@pytest.mark.parametrize("api", transpose_apis)
def test_small_matrix(client, api):
    matrix = [[1]]
    response = client.post(api, json=matrix)
    assert response.status_code == 200
    assert response.json == [[1]]


@pytest.mark.parametrize("api", transpose_apis)
def test_negative_decimal_matrix(client, api):
    matrix = [[-1, 2, 3.3], [4, -5.7, 6], [7.0, 8, -9]]
    response = client.post(api, json=matrix)
    assert response.status_code == 200
    assert response.json == [[-1, 4, 7.0], [2, -5.7, 8], [3.3, 6, -9]]


@pytest.mark.parametrize("api", transpose_apis)
def test_matrix_string(client, api):
    matrix = "[[1,2,3],[4,5,6],[7,8,9]]"
    response = client.post(api, data=matrix, content_type="application/json")
    assert response.status_code == 200
    assert response.json == [[1, 4, 7], [2, 5, 8], [3, 6, 9]]


@pytest.mark.skip(reason="Undefined behavior for invalid matrix inputs")
@pytest.mark.parametrize("api", transpose_apis)
def test_matrix_string_invalid(client, api):
    matrix = "[[1,3],[4,5,6[7,8,9]"
    response = client.post(api, data=matrix, content_type="application/json")
    assert response.status_code == 200
    assert response.json == [[1, 4, 7], [2, 5, 8], [3, 6, 9]]


@pytest.mark.skip(reason="Undefined behavior for invalid matrix inputs")
@pytest.mark.parametrize("api", transpose_apis)
def test_special_cases(client, api):
    matrix = [["abc", None, {}], [True, False, 23], [-7.3, inf, bytes(127)]]
    response = client.post(api, json=matrix)
    assert response.status_code == 200
    assert response.json == [
        ["abc", True, -7.3],
        [None, False, inf],
        [{}, 23, bytes(127)],
    ]
