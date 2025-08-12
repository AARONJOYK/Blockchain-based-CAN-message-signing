// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ECUVerification {
    mapping(bytes32 => address) public ecuAddresses;
    mapping(bytes32 => bool) public verifiedPayloads;

    event Debug(address recovered, address expected, bool valid);
    event PayloadVerified(bytes32 indexed payloadHash, bytes32 indexed ecuId, bool valid);

    function registerECU(bytes32 ecuId, address ecuAddr) public {
        ecuAddresses[ecuId] = ecuAddr;
    }

    function verifyPayload(
        bytes32 ecuId,
        string memory payload,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public returns (bool) {
        bytes32 hash = keccak256(bytes(payload));
        bytes32 prefixed = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", hash));
        address recovered = ecrecover(prefixed, v, r, s);
        bool valid = (recovered == ecuAddresses[ecuId]);

        verifiedPayloads[hash] = valid;

        emit Debug(recovered, ecuAddresses[ecuId], valid);
        emit PayloadVerified(hash, ecuId, valid);

        return valid;
    }

    function getVerificationResult(string memory payload) public view returns (bool) {
        return verifiedPayloads[keccak256(bytes(payload))];
    }
}
