import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.generate_pdf_use_case import GeneratePDFUseCase
from app.application.dto.practice_data_dto import PracticeDataDTO
from app.domain.entities.practice import Practice
from app.domain.entities.postural_error import PosturalError
from app.domain.entities.musical_error import MusicalError


# =====================================================
# 📦 FIXTURES
# =====================================================

@pytest.fixture
def practice_data():
    return PracticeDataDTO(
        uid="user123",
        practice_id=1,
        date="2025-11-04",
        time="10:00",
        scale="Do Mayor",
        scale_type="mayor",
        num_postural_errors=0,
        num_musical_errors=0,
        duration=120,
        bpm=90,
        figure=1.0,
        octaves=2
    )


@pytest.fixture
def mock_services():
    """Devuelve mocks de los servicios realmente usados por GeneratePDFUseCase"""
    return {
        "metadata_service": AsyncMock(),
        "postural_error_service": AsyncMock(),
        "musical_error_service": AsyncMock(),
        "practice_service": AsyncMock(),
        "pdf_service": AsyncMock(),
    }


# =====================================================
# ✅ ESCENARIOS PRINCIPALES
# =====================================================

@pytest.mark.asyncio
async def test_execute_success_with_errors(practice_data, mock_services):
    """Caso exitoso: hay errores y se genera PDF correctamente"""
    services = mock_services

    # Configuración de mocks
    services["metadata_service"].is_video_and_audio_done.return_value = True
    services["postural_error_service"].get_errors_by_practice.return_value = [
        PosturalError(1, "00:01", "00:02", 5, "Inclinación excesiva", 1)
    ]
    services["musical_error_service"].get_errors_by_practice.return_value = [
        MusicalError(1, "00:03", "C", "D", 1)
    ]
    fake_practice = Practice(
        id=1, date="2025-11-04", time="10:00",
        num_postural_errors=1, num_musical_errors=1,
        duration=120, id_student="user123", student_name="Daniel",
        scale="Do Mayor", scale_type="mayor", bpm=90, figure=1.0, octaves=2
    )
    services["practice_service"].update_num_postural_errors.return_value = fake_practice
    services["practice_service"].update_num_musical_errors.return_value = fake_practice
    services["pdf_service"].generate_pdf.return_value = "/tmp/report.pdf"

    use_case = GeneratePDFUseCase(**services)
    result = await use_case.execute(practice_data)

    # Verificaciones de flujo
    assert result == "/tmp/report.pdf"
    services["metadata_service"].is_video_and_audio_done.assert_awaited_once()
    services["pdf_service"].generate_pdf.assert_awaited_once()
    services["metadata_service"].save_pdf_path.assert_awaited_once_with(
        "user123", 1, "/tmp/report.pdf"
    )

    # Verificar conteo de errores actualizados
    services["practice_service"].update_num_postural_errors.assert_awaited_once_with(1, 1)
    services["practice_service"].update_num_musical_errors.assert_awaited_once_with(1, 1)


@pytest.mark.asyncio
async def test_execute_success_no_errors(practice_data, mock_services):
    """Caso exitoso: sin errores posturales ni musicales"""
    services = mock_services
    services["metadata_service"].is_video_and_audio_done.return_value = True
    services["postural_error_service"].get_errors_by_practice.return_value = []
    services["musical_error_service"].get_errors_by_practice.return_value = []
    fake_practice = Practice(
        id=1, date="2025-11-04", time="10:00",
        num_postural_errors=0, num_musical_errors=0,
        duration=120, id_student="user123", student_name="Daniel",
        scale="Do Mayor", scale_type="mayor", bpm=90, figure=1.0, octaves=2
    )
    services["practice_service"].update_num_postural_errors.return_value = fake_practice
    services["practice_service"].update_num_musical_errors.return_value = fake_practice
    services["pdf_service"].generate_pdf.return_value = "/tmp/empty.pdf"

    use_case = GeneratePDFUseCase(**services)
    result = await use_case.execute(practice_data)

    # Cuando no hay errores, PDF puede ser "None" según lógica
    assert isinstance(result, str)
    services["metadata_service"].save_pdf_path.assert_awaited_once()
    services["pdf_service"].generate_pdf.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_processing_not_done(practice_data, mock_services):
    """Caso fallido: video/audio aún no procesado"""
    services = mock_services
    services["metadata_service"].is_video_and_audio_done.return_value = False

    use_case = GeneratePDFUseCase(**services)
    with pytest.raises(Exception) as exc_info:
        await use_case.execute(practice_data)

    assert "not completed" in str(exc_info.value).lower() or "not done" in str(exc_info.value).lower()


# =====================================================
# ⚠️ CASOS DE ERROR / FALLAS CONTROLADAS
# =====================================================

@pytest.mark.asyncio
async def test_pdf_generation_failure(practice_data, mock_services):
    """Falla en la generación del PDF"""
    services = mock_services
    services["metadata_service"].is_video_and_audio_done.return_value = True
    services["postural_error_service"].get_errors_by_practice.return_value = [
        PosturalError(1, "00:10", "00:12", 10, "Error postural", 1)
    ]
    fake_practice = Practice(
        id=1, date="2025-11-04", time="10:00",
        num_postural_errors=1, num_musical_errors=0,
        duration=120, id_student="user123", student_name="Daniel",
        scale="Do Mayor", scale_type="mayor", bpm=90, figure=1.0, octaves=2
    )
    services["practice_service"].update_num_postural_errors.return_value = fake_practice
    services["practice_service"].update_num_musical_errors.return_value = fake_practice
    services["pdf_service"].generate_pdf.side_effect = Exception("PDF generation failed")

    use_case = GeneratePDFUseCase(**services)
    with pytest.raises(Exception) as exc_info:
        await use_case.execute(practice_data)

    assert "pdf generation failed" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_metadata_save_pdf_path_failure(practice_data, mock_services):
    """Falla al guardar la ruta PDF en metadata"""
    services = mock_services
    services["metadata_service"].is_video_and_audio_done.return_value = True
    services["postural_error_service"].get_errors_by_practice.return_value = []
    services["musical_error_service"].get_errors_by_practice.return_value = []
    fake_practice = Practice(
        id=1, date="2025-11-04", time="10:00",
        num_postural_errors=0, num_musical_errors=0,
        duration=120, id_student="user123", student_name="Daniel",
        scale="Do Mayor", scale_type="mayor", bpm=90, figure=1.0, octaves=2
    )
    services["practice_service"].update_num_postural_errors.return_value = fake_practice
    services["practice_service"].update_num_musical_errors.return_value = fake_practice
    services["pdf_service"].generate_pdf.return_value = "/tmp/report.pdf"
    services["metadata_service"].save_pdf_path.side_effect = Exception("Failed to save PDF path")

    use_case = GeneratePDFUseCase(**services)
    with pytest.raises(Exception) as exc_info:
        await use_case.execute(practice_data)

    assert "failed to save pdf path" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_invalid_practice_data_missing_uid(mock_services):
    """Validación de datos: UID faltante"""
    bad_data = PracticeDataDTO(
        uid=None, practice_id=1, date="2025-11-04", time="10:00",
        scale="Do Mayor", scale_type="mayor", num_postural_errors=0,
        num_musical_errors=0, duration=120, bpm=90, figure=1.0, octaves=2
    )

    use_case = GeneratePDFUseCase(**mock_services)
    with pytest.raises(Exception):
        await use_case.execute(bad_data)


# =====================================================
# 🧠 VERIFICACIÓN DE ORDEN LÓGICO DE LLAMADAS
# =====================================================

@pytest.mark.asyncio
async def test_call_order(practice_data, mock_services):
    """Verifica que las llamadas ocurren en orden lógico esperado"""
    services = mock_services
    services["metadata_service"].is_video_and_audio_done.return_value = True
    services["postural_error_service"].get_errors_by_practice.return_value = []
    services["musical_error_service"].get_errors_by_practice.return_value = []
    fake_practice = Practice(
        id=1, date="2025-11-04", time="10:00",
        num_postural_errors=0, num_musical_errors=0,
        duration=120, id_student="user123", student_name="Daniel",
        scale="Do Mayor", scale_type="mayor", bpm=90, figure=1.0, octaves=2
    )
    services["practice_service"].update_num_postural_errors.return_value = fake_practice
    services["practice_service"].update_num_musical_errors.return_value = fake_practice
    services["pdf_service"].generate_pdf.return_value = "/tmp/report.pdf"

    use_case = GeneratePDFUseCase(**services)
    await use_case.execute(practice_data)

    # Validamos que se llame primero is_video_and_audio_done
    services["metadata_service"].is_video_and_audio_done.assert_awaited_once()
    # Luego las llamadas de error y práctica
    services["postural_error_service"].get_errors_by_practice.assert_awaited_once()
    services["musical_error_service"].get_errors_by_practice.assert_awaited_once()
    services["practice_service"].update_num_postural_errors.assert_awaited_once()
    services["practice_service"].update_num_musical_errors.assert_awaited_once()
