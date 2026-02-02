"""
Unit tests for MCP client initialization and tool calls.

Tests cover:
- Client connection/disconnection
- Tool call execution
- Error handling
- Context manager usage
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from uuid import uuid4

from app.mcp.client import MCPClient, get_mcp_client, shutdown_mcp_client


class TestMCPClient:
    """Unit tests for MCPClient class."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test MCPClient initializes with no connection."""
        client = MCPClient()

        assert client.session is None
        assert client._read_stream is None
        assert client._write_stream is None

    @pytest.mark.asyncio
    async def test_client_connect(self):
        """Test MCPClient establishes connection."""
        client = MCPClient()

        with patch('app.mcp.client.stdio_client') as mock_stdio:
            # Mock stdio streams
            mock_read = AsyncMock()
            mock_write = AsyncMock()
            mock_stdio.return_value = (mock_read, mock_write)

            with patch('app.mcp.client.ClientSession') as mock_session_class:
                mock_session = AsyncMock()
                mock_session_class.return_value = mock_session

                await client.connect()

                assert client.session is not None
                assert client._read_stream == mock_read
                assert client._write_stream == mock_write
                mock_session.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_client_connect_idempotent(self):
        """Test MCPClient.connect() is idempotent (doesn't reconnect if already connected)."""
        client = MCPClient()

        with patch('app.mcp.client.stdio_client') as mock_stdio:
            mock_read = AsyncMock()
            mock_write = AsyncMock()
            mock_stdio.return_value = (mock_read, mock_write)

            with patch('app.mcp.client.ClientSession') as mock_session_class:
                mock_session = AsyncMock()
                mock_session_class.return_value = mock_session

                # First connect
                await client.connect()

                # Second connect should not recreate session
                await client.connect()

                # Session created only once
                mock_session_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_client_disconnect(self):
        """Test MCPClient disconnects cleanly."""
        client = MCPClient()

        with patch('app.mcp.client.stdio_client'):
            with patch('app.mcp.client.ClientSession') as mock_session_class:
                mock_session = AsyncMock()
                mock_session_class.return_value = mock_session

                await client.connect()
                await client.disconnect()

                assert client.session is None
                assert client._read_stream is None
                assert client._write_stream is None

    @pytest.mark.asyncio
    async def test_call_tool_success(self):
        """Test successful tool call."""
        client = MCPClient()

        # Mock connected session
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_content = Mock()
        mock_content.text = '{"task_id": "123", "title": "Test"}'
        mock_result.content = [mock_content]
        mock_session.call_tool.return_value = mock_result

        client.session = mock_session

        result = await client.call_tool("add_task", {"title": "Test"})

        assert result == '{"task_id": "123", "title": "Test"}'
        mock_session.call_tool.assert_called_once_with("add_task", {"title": "Test"})

    @pytest.mark.asyncio
    async def test_call_tool_not_connected(self):
        """Test call_tool raises error if not connected."""
        client = MCPClient()

        with pytest.raises(RuntimeError, match="not connected"):
            await client.call_tool("add_task", {})

    @pytest.mark.asyncio
    async def test_call_tool_handles_error(self):
        """Test call_tool handles and re-raises errors."""
        client = MCPClient()

        mock_session = AsyncMock()
        mock_session.call_tool.side_effect = Exception("Tool error")
        client.session = mock_session

        with pytest.raises(Exception, match="Tool error"):
            await client.call_tool("add_task", {})


class TestGetMCPClient:
    """Unit tests for get_mcp_client context manager."""

    @pytest.mark.asyncio
    async def test_get_client_creates_instance(self):
        """Test get_mcp_client creates client on first use."""
        with patch('app.mcp.client._mcp_client', None):
            with patch('app.mcp.client.MCPClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.session = None
                mock_client_class.return_value = mock_client

                with patch('app.mcp.client.stdio_client'):
                    with patch('app.mcp.client.ClientSession'):
                        async with get_mcp_client() as client:
                            assert client is not None
                            # Should connect on first use
                            mock_client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_reuses_instance(self):
        """Test get_mcp_client reuses existing client."""
        # Create a mock client that's already connected
        mock_client = AsyncMock()
        mock_client.session = Mock()  # Already connected

        with patch('app.mcp.client._mcp_client', mock_client):
            async with get_mcp_client() as client:
                assert client == mock_client
                # Should not reconnect
                mock_client.connect.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_client_handles_error(self):
        """Test get_mcp_client handles errors without disconnecting."""
        mock_client = AsyncMock()
        mock_client.session = Mock()
        mock_client.call_tool.side_effect = Exception("Tool error")

        with patch('app.mcp.client._mcp_client', mock_client):
            with pytest.raises(Exception, match="Tool error"):
                async with get_mcp_client() as client:
                    await client.call_tool("add_task", {})

            # Client should still exist (not disconnected)
            assert mock_client is not None


class TestShutdownMCPClient:
    """Unit tests for shutdown_mcp_client function."""

    @pytest.mark.asyncio
    async def test_shutdown_disconnects_client(self):
        """Test shutdown_mcp_client disconnects active client."""
        mock_client = AsyncMock()

        with patch('app.mcp.client._mcp_client', mock_client):
            await shutdown_mcp_client()

            mock_client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_handles_no_client(self):
        """Test shutdown_mcp_client handles case with no active client."""
        with patch('app.mcp.client._mcp_client', None):
            # Should not raise error
            await shutdown_mcp_client()


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
