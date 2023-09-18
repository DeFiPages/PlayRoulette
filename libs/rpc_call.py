from defichain import Node



def transferdomain(node: Node, src_address: str, amount: str, dst_address: str, to_dvm: bool = False) -> str:
    """
    Creates (and submits to local node and network) a transaction to transfer assets across domains,
    either from DVM to EVM or vice versa.

    :param node: (required) The local node to which the transaction will be submitted.
    :type node: Node
    :param src_address: (required) The source address from which the assets will be transferred.
    :type src_address: str
    :param amount: (required) The amount transferred in the format "amount@token", e.g. "1.0@DFI".
    :type amount: str
    :param dst_address: (required) The destination address to which the assets will be transferred.
    :type dst_address: str
    :param to_dvm: (optional) False if transferring from DVM to EVM, True if transferring from EVM to DVM. Default is False.
    :type to_dvm: bool
    :return: "hash" (string) -- The hex-encoded hash of the broadcasted transaction.

    :example:

        >>> transferdomain("<DFI_address>", "1.0@DFI", "<ETH_address>")
        >>> transferdomain("<ETH_address>", "1.0@DFI", "<DFI_address>", to_evm=False)

    Note: This function encapsulates the RPC call:
    defi-cli transferdomain '[{"src":{"address":"<DFI_address>", "amount":"1.0@DFI", "domain": 2}, "dst":{"address":"<ETH_address>", "amount":"1.0@DFI", "domain": 3}}]'
    defi-cli transferdomain '[{"src":{"address":"<ETH_address>", "amount":"1.0@DFI", "domain": 3}, "dst":{"address":"<DFI_address>", "amount":"1.0@DFI", "domain": 2}}]'
    """
    src_domain = 3 if to_dvm else 2  # 2 for DVM and 3 for EVM
    dst_domain = 2 if to_dvm else 3  # reversed from source domain


    transaction = [{
        "src": {
            "address": src_address,
            "amount": amount,
            "domain": src_domain,
        },
        "dst": {
            "address": dst_address,
            "amount": amount,
            "domain": dst_domain,
        }
    }]
    return node._rpc.call("transferdomain", transaction)